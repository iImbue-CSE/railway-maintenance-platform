# railway-maintenance-platform

## 3D railway digital twin

The browser-based 3D prototype is in `visualization/`:

```bash
cd visualization
PYTHONPATH=. python3 visualize_3d.py
open railway_model_3d.html
```

The generated model uses Three.js from a public CDN, so an internet
connection is needed when opening the HTML file. The current visualization
is a standalone demonstration; backend/API wiring can be added next.