## Defects detection app (WIP)

App based on Python + JS + Flask + YOLO + OpenCV + numpy + asyncio


### Requiements:

- Flask==3.0.3
- opencv-python==4.10.0.84
- ultralitics==8.0.196


### Run:

```bash
python main.py
```

### Use:

Example files to load - see in examples/ dir.

As web app - via http://127.0.0.1:4455

Examples of request to REST API:
```bash
curl -s -X POST -F filedata=@code557.jpg http://127.0.0.1:4455/api
```
or with beautifing:
```bash
curl -s -X POST -F filedata=@code706.jpg -F indent=4 http://127.0.0.1:4455/api
```
or with full pathname and via external addrrss:
```bash
curl -s -X POST -F filedata=@S:\tmpp\cvat_export\uploads\code5129.jpg -F indent=4 https://cvat.sphynkx.org.ua/api
```
