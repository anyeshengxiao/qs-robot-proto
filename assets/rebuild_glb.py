# -*- coding: utf-8 -*-
"""把 draco 压缩的小舆 GLB 重打包为「未压缩几何 + 降采样贴图」的小体积 GLB"""
import struct, json, io, math, pathlib
import numpy as np
import DracoPy
from PIL import Image

ROOT = pathlib.Path(r'C:\Users\52560\Documents\Kimi\Workspaces\机器人\qs-robot-proto')
SRC = ROOT / 'assets' / 'xiaoyu.glb'
DST = ROOT / 'assets' / 'xiaoyu_slim.glb'

d = SRC.read_bytes()
clen, ctype = struct.unpack('<II', d[12:20])
gltf = json.loads(d[20:20 + clen])
# BIN chunk
off = 20 + clen
blen, btype = struct.unpack('<II', d[off:off + 8])
BIN = d[off + 8: off + 8 + blen]

prim = gltf['meshes'][0]['primitives'][0]
draco = prim['extensions']['KHR_draco_mesh_compression']
bv = gltf['bufferViews'][draco['bufferView']]
draco_buf = BIN[bv.get('byteOffset', 0): bv.get('byteOffset', 0) + bv['byteLength']]

mesh = DracoPy.decode(draco_buf)
pts = np.array(mesh.points, dtype=np.float32).reshape(-1, 3)
faces = np.array(mesh.faces, dtype=np.uint32).reshape(-1, 3)
print('verts:', len(pts), 'faces:', len(faces))
nrm = getattr(mesh, 'normals', None)
uv = getattr(mesh, 'tex_coords', None)
if uv is None or len(uv) == 0:
    uv = getattr(mesh, 'tex_coord', None)
nrm = np.array(nrm, dtype=np.float32).reshape(-1, 3) if (nrm is not None and len(nrm) > 0) else None
uv = np.array(uv, dtype=np.float32).reshape(-1, 2) if (uv is not None and len(uv) > 0) else None
print('normals:', None if nrm is None else nrm.shape, 'uv:', None if uv is None else uv.shape)
if nrm is None or len(nrm) != len(pts):
    # 计算顶点法线
    n = np.zeros_like(pts)
    tri = pts[faces]
    fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    for i in range(3):
        np.add.at(n, faces[:, i], fn)
    ln = np.linalg.norm(n, axis=1, keepdims=True); ln[ln == 0] = 1
    nrm = (n / ln).astype(np.float32)
if uv is None or len(uv) != len(pts):
    uv = np.zeros((len(pts), 2), dtype=np.float32)

# ---- 贴图降采样 ----
def load_img(idx, max_side):
    img = gltf['images'][idx]
    bv = gltf['bufferViews'][img['bufferView']]
    raw = BIN[bv.get('byteOffset', 0): bv.get('byteOffset', 0) + bv['byteLength']]
    im = Image.open(io.BytesIO(raw))
    im.load()
    print('img', idx, im.size, im.mode, '->', end=' ')
    if max(im.size) > max_side:
        r = max_side / max(im.size)
        im = im.resize((max(1, int(im.size[0] * r)), max(1, int(im.size[1] * r))), Image.LANCZOS)
    buf = io.BytesIO()
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA') if im.mode != 'P' else im.convert('RGBA')
        im.save(buf, 'PNG', optimize=True)
        mime = 'image/png'
    else:
        im.convert('RGB').save(buf, 'PNG', optimize=True)
        mime = 'image/png'
    out = buf.getvalue()
    print(im.size, mime, round(len(out) / 1048576, 2), 'MB')
    return out, mime

mat = gltf['materials'][0]
tex_roles = {}  # texture index -> (json key)
for k in ('normalTexture', 'emissiveTexture', 'occlusionTexture'):
    if k in mat: tex_roles[mat[k]['index']] = k
if 'pbrMetallicRoughness' in mat:
    pbr = mat['pbrMetallicRoughness']
    if 'baseColorTexture' in pbr: tex_roles[pbr['baseColorTexture']['index']] = 'baseColorTexture'
    if 'metallicRoughnessTexture' in pbr: tex_roles[pbr['metallicRoughnessTexture']['index']] = 'metallicRoughnessTexture'

img_data = []   # per source image: (bytes, mime)
tex_map = {}    # old texture idx -> new texture idx
new_textures = []
for ti, tex in enumerate(gltf['textures']):
    src = tex['source']
    role = tex_roles.get(ti, '')
    max_side = 1024 if role in ('baseColorTexture', 'normalTexture') else 512
    data, mime = load_img(src, max_side)
    img_data.append((data, mime))
    tex_map[ti] = len(new_textures)
    new_textures.append({'source': len(img_data) - 1, 'sampler': 0})

# ---- 组装新 GLB ----
bin_parts = []
def add_bin(data):
    off = sum(len(p) for p in bin_parts)
    bin_parts.append(data)
    pad = (4 - len(data) % 4) % 4
    if pad: bin_parts.append(b'\x00' * pad)
    return off, len(data)

views, accessors = [], []
def add_accessor(arr, ctype, atype, target, minmax=False):
    raw = arr.tobytes()
    o, l = add_bin(raw)
    views.append({'buffer': 0, 'byteOffset': o, 'byteLength': l, 'target': target})
    acc = {'bufferView': len(views) - 1, 'componentType': ctype,
           'count': len(arr), 'type': atype}
    if minmax:
        acc['min'] = [float(x) for x in arr.min(axis=0)]
        acc['max'] = [float(x) for x in arr.max(axis=0)]
    accessors.append(acc)
    return len(accessors) - 1

idx_acc = add_accessor(faces.reshape(-1), 5125, 'SCALAR', 34963)
pos_acc = add_accessor(pts, 5126, 'VEC3', 34962, minmax=True)
nrm_acc = add_accessor(nrm, 5126, 'VEC3', 34962)
uv_acc = add_accessor(uv, 5126, 'VEC2', 34962)

new_images = []
for data, mime in img_data:
    o, l = add_bin(data)
    views.append({'buffer': 0, 'byteOffset': o, 'byteLength': l})
    new_images.append({'bufferView': len(views) - 1, 'mimeType': mime})

new_mat = {'name': mat.get('name', 'mat'), 'pbrMetallicRoughness': {'metallicFactor': 0.4, 'roughnessFactor': 0.6}}
if 'pbrMetallicRoughness' in mat:
    pbr = mat['pbrMetallicRoughness']
    if 'baseColorTexture' in pbr:
        new_mat['pbrMetallicRoughness']['baseColorTexture'] = {'index': tex_map[pbr['baseColorTexture']['index']]}
    if 'metallicRoughnessTexture' in pbr:
        new_mat['pbrMetallicRoughness']['metallicRoughnessTexture'] = {'index': tex_map[pbr['metallicRoughnessTexture']['index']]}
    if 'baseColorFactor' in pbr:
        new_mat['pbrMetallicRoughness']['baseColorFactor'] = pbr['baseColorFactor']
if 'normalTexture' in mat:
    new_mat['normalTexture'] = {'index': tex_map[mat['normalTexture']['index']]}
if 'emissiveFactor' in mat:
    new_mat['emissiveFactor'] = mat['emissiveFactor']
if 'emissiveTexture' in mat:
    new_mat['emissiveTexture'] = {'index': tex_map[mat['emissiveTexture']['index']]}
new_mat['doubleSided'] = bool(mat.get('doubleSided'))

new_gltf = {
    'asset': {'version': '2.0', 'generator': 'qs-rebuild'},
    'scene': 0,
    'scenes': [{'nodes': [0]}],
    'nodes': [{'mesh': 0, 'rotation': [0.7071068286895752, 0, 0, 0.7071068286895752]}],
    'meshes': [{'primitives': [{'attributes': {'POSITION': pos_acc, 'NORMAL': nrm_acc, 'TEXCOORD_0': uv_acc},
                                 'indices': idx_acc, 'material': 0, 'mode': 4}]}],
    'materials': [new_mat],
    'textures': new_textures,
    'images': new_images,
    'samplers': [{'magFilter': 9729, 'minFilter': 9987, 'wrapS': 10497, 'wrapT': 10497}],
    'accessors': accessors,
    'bufferViews': views,
}
bin_blob = b''.join(bin_parts)
new_gltf['buffers'] = [{'byteLength': len(bin_blob)}]

js = json.dumps(new_gltf, separators=(',', ':')).encode('utf-8')
js += b' ' * ((4 - len(js) % 4) % 4)
bin_blob += b'\x00' * ((4 - len(bin_blob) % 4) % 4)
total = 12 + 8 + len(js) + 8 + len(bin_blob)
out = struct.pack('<III', 0x46546C67, 2, total)
out += struct.pack('<II', len(js), 0x4E4F534A) + js
out += struct.pack('<II', len(bin_blob), 0x004E4942) + bin_blob
DST.write_bytes(out)
print('NEW GLB MB:', round(len(out) / 1048576, 2))
