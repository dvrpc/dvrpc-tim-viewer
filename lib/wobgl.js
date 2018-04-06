function createWebGLCanvas(map) {
    var canvas = document.createElement("canvas");
    var mapCanvas = map.getCanvas();
    var mapCanvasContainer = map.getCanvasContainer();

    canvas.id = "wobgl";
    canvas.width = mapCanvas.width,
    canvas.height = mapCanvas.height;

    mapCanvasContainer.appendChild(canvas);
    return canvas;
}

var canvas = createWebGLCanvas(map);
// map.getCenter(), map.getZoom(), map.getPitch(), map.getBearing()
var gl = canvas.getContext("webgl");
console.log(canvas, gl);
