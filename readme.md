# PDF to Manifest

A sample script to extract images from a PDF and create a single manifest for the PDF. 

It also generates static image pyramid so that there is no need for an image-server.

```bash
pip install -r requirements.txt
python main.py /path/to/pdf.pdf
```

## Testing

For local testing, use a tool like [http-server](https://www.npmjs.com/package/http-server) for running local http-server in `/output/iiif` directory.

```bash
cd output/iiif
http-server -p 8000 --cors
```

The manifest should then render in a viewer, e.g. https://uv-v4.netlify.app/#?c=&m=&cv=1&manifest=http%3A%2F%2Flocalhost%3A8000%2Fmanifest.json