
function createWebGLCanvas(map) {
    var canvas = document.createElement("canvas");
    var mapCanvas = map.getCanvas();
    var mapCanvasContainer = map.getCanvasContainer();

    canvas.id = "wobgl";
    // canvas.class = "mapboxgl-canvas";
    canvas.width = mapCanvas.width,
    canvas.height = mapCanvas.height;

    mapCanvasContainer.appendChild(canvas);

    return canvas;
}


class WobGL {
    constructor(map) {
        this.map = map;

        this.mapCanvas = null;
        this.canvas = null;

        window.addEventListener("resize", evt => this._onWindowResize, false);

        this.createWebGLCanvas();
    }
    createWebGLCanvas() {
        this.canvas = document.createElement("canvas");
        this.mapCanvas = this.map.getCanvas();
        var mapCanvasContainer = this.map.getCanvasContainer();
        this.canvas.id = "wobgl";

        mapCanvasContainer.appendChild(this.canvas);
    }
    
    _resize() {
        
        this.canvas.width = this.mapCanvas.width;
        this.canvas.height = this.mapCanvas.height;
        console.log(this.canvas.width, this.canvas.height);
    }
    _onWindowResize() {
        // console.log(this.map);
        this._resize();
    }
    
}

// var wobgl = {
    
    // canvas: createWebGLCanvas(map),
    // gl: this.canvas.getContext("webgl"),
    // _resize: function () {
        // console.log("this", this);
        // console.log("this.canvas", this.canvas);
    // },
// };

function randomInt(range) {
    return Math.floor(Math.random() * range);
}
function round(value, significance) {
    return Math.round(value * 10 ** significance) / (10 ** significance);
}
function LatLongToPixelXY(latitude, longitude) {
    var pi_180 = Math.PI / 180.0;
    var pi_4 = Math.PI * 4;
    var sinLatitude = Math.sin(latitude * pi_180);
    var pixelY = (0.5 - Math.log((1 + sinLatitude) / (1 - sinLatitude)) / (pi_4)) * 256;
    var pixelX = ((longitude + 180) / 360) * 256;
    var pixel = { x: pixelX, y: pixelY };
    return pixel;
}
function translateMatrix(matrix, tx, ty) {
    // translation is in last column of matrix
    matrix[12] += matrix[0] * tx + matrix[4] * ty;
    matrix[13] += matrix[1] * tx + matrix[5] * ty;
    matrix[14] += matrix[2] * tx + matrix[6] * ty;
    matrix[15] += matrix[3] * tx + matrix[7] * ty;
}
function scaleMatrix(matrix, scaleX, scaleY) {
    // scaling x and y, which is just scaling first two columns of matrix
    matrix[0] *= scaleX;
    matrix[1] *= scaleX;
    matrix[2] *= scaleX;
    matrix[3] *= scaleX;
    matrix[4] *= scaleY;
    matrix[5] *= scaleY;
    matrix[6] *= scaleY;
    matrix[7] *= scaleY;
}

// wobgl.canvas = createWebGLCanvas(map);
// wobgl.gl = wobgl.canvas.getContext("webgl");

// window.addEventListener("resize", wobgl._resize);
// document.addEventListener("resize", wobgl._resize);

// map.getCenter(), map.getZoom(), map.getPitch(), map.getBearing()

// console.log(canvas, gl);

var wobgl = new WobGL(map);