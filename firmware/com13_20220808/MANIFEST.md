# 校验清单 MANIFEST（rootfs 全量备份 · 21 文件）

> 由 `python tools/_mkmanifest.py` 生成；SHA256 基于文件原始字节。
> 用途：日后核对 `firmware/com13_20220808/rootfs/` 是否与 2026-09-26 从实机 COM13 的这次全量备份 一致。

| 文件 | 大小(B) | SHA256 |
|---|---:|---|
| `actuator_led.mpy` | 2309 | `047770d0dfd138b8293cb8ccf08347abaa4dd60f2d6c479a3176db2648aa0f5d` |
| `alert.dat` | 20782 | `24e951ce68127338f235530dbaf9fe13812989506db634fe33e7ea14a3d6b4df` |
| `basic.mpy` | 3154 | `37a517bf5788d1138b0e08bdda08d26496fe6ca513828043d39eca64ea7eab06` |
| `boot.py` | 139 | `16f5b4bcb120e9a032242b47967e649a0cc577b41939e81ef7d4b4da181bd17f` |
| `broken.dat` | 44974 | `1ee1ef75337068215f6c16a9eb6d7e0def69923ea308e388d1fc5d6600c0f3aa` |
| `control_board_v1.mpy` | 8265 | `bf6527eed29a35316bc8735acd8eedce6074ebf9b1831fcae5ce3b0948f0180d` |
| `drop.dat` | 27694 | `fb8021a6519c662a5fb64f2c7c30be5f44fefbb8fe3619d08edbbd8bc020f3e8` |
| `du.dat` | 16322 | `5910045b88fe222801529832857e2cb335a24d8ef645482382c24e791cb1a7ea` |
| `electric.dat` | 37486 | `3bf8ae7ed29dc32720a9ef26f409a96f4741354020dc2a1d824f98b8b1159f54` |
| `funny.dat` | 26542 | `2205cd7e6767dfaa869b99cd6053ad1ca2b86b9e5ea3a899ec47733dc21cba40` |
| `main.py` | 1360 | `dead061bb451eeff950d315c0c79584e78801dcc4fbe09e748b6413b8d5386ff` |
| `msg.dat` | 17686 | `abc95dfe2b63fbd5a91f60caa6aebfbb79a06fe3d69d6761f5f80324021d1388` |
| `pass.dat` | 18478 | `1e4130ca5248635e7d50fb48510fd4c3c5a8f50f27ce50714ee7fb4547c9c457` |
| `r1.dat` | 364544 | `91fa56353ef523488f300dcf745bbac518751d1ccc882cd40b1fd1f5ba777099` |
| `record_end.dat` | 17686 | `9f3e268048fb401c1c64c35282f7311a36a45f7b165853e34f05f905706e61bb` |
| `record_start.dat` | 21428 | `d4f4194defd403becce65133eb0b7b7427ad70e85d1d166be71c820234113298` |
| `right.dat` | 20782 | `462b3b1b9e14536526e73e6356e03155b3e036b2c6f9e8d9c4f4978ebb58a431` |
| `sensor_infrared.mpy` | 215 | `ebba8c5a9d85bd8c465b0852bd131a21177ee52116635d740103ab7a0dda4c68` |
| `tech.dat` | 29422 | `c70e12b4be13315be88115ea1a5d3fe5763d9bb65b5607c842ce24ecefadd845` |
| `variable.py` | 63 | `e64f6ec5e3694b6fef857b17b296f323e9a668d7b09a3702981b1458f36e1a7c` |
| `wrong.dat` | 24812 | `6c23da88eba5d122ec865213b7adbe285250cccd99485bfffef94dece0ee2ad9` |

**合计：21 个文件，704143 字节（687.6 KB）**

## 校验方法

重新计算并打印当前 rootfs 的 SHA256，与上面逐行比对即可：

```powershell
python -c "import hashlib,os; \
root=r'firmware/com13_20220808/rootfs'; \
[print(hashlib.sha256(open(os.path.join(d,f),'rb').read()).hexdigest(), os.path.relpath(os.path.join(d,f),root)) \
 for d,_,fs in os.walk(root) for f in fs]"
```
