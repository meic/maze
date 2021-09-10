WALKING_SVG = {
    data: "M208 96c26.5 0 48-21.5 48-48S234.5 0 208 0s-48 21.5-48 48 21.5 48 48 48zm94.5 149.1l-23.3-11.8-9.7-29.4c-14.7-44.6-55.7-75.8-102.2-75.9-36-.1-55.9 10.1-93.3 25.2-21.6 8.7-39.3 25.2-49.7 46.2L17.6 213c-7.8 15.8-1.5 35 14.2 42.9 15.6 7.9 34.6 1.5 42.5-14.3L81 228c3.5-7 9.3-12.5 16.5-15.4l26.8-10.8-15.2 60.7c-5.2 20.8.4 42.9 14.9 58.8l59.9 65.4c7.2 7.9 12.3 17.4 14.9 27.7l18.3 73.3c4.3 17.1 21.7 27.6 38.8 23.3 17.1-4.3 27.6-21.7 23.3-38.8l-22.2-89c-2.6-10.3-7.7-19.9-14.9-27.7l-45.5-49.7 17.2-68.7 5.5 16.5c5.3 16.1 16.7 29.4 31.7 37l23.3 11.8c15.6 7.9 34.6 1.5 42.5-14.3 7.7-15.7 1.4-35.1-14.3-43zM73.6 385.8c-3.2 8.1-8 15.4-14.2 21.5l-50 50.1c-12.5 12.5-12.5 32.8 0 45.3s32.7 12.5 45.2 0l59.4-59.4c6.1-6.1 10.9-13.4 14.2-21.5l13.5-33.8c-55.3-60.3-38.7-41.8-47.4-53.7l-20.7 51.5z",
    height: 512,
    width: 320,
}

BOOK_SVG = {
    data: "M542.22 32.05c-54.8 3.11-163.72 14.43-230.96 55.59-4.64 2.84-7.27 7.89-7.27 13.17v363.87c0 11.55 12.63 18.85 23.28 13.49 69.18-34.82 169.23-44.32 218.7-46.92 16.89-.89 30.02-14.43 30.02-30.66V62.75c.01-17.71-15.35-31.74-33.77-30.7zM264.73 87.64C197.5 46.48 88.58 35.17 33.78 32.05 15.36 31.01 0 45.04 0 62.75V400.6c0 16.24 13.13 29.78 30.02 30.66 49.49 2.6 149.59 12.11 218.77 46.95 10.62 5.35 23.21-1.94 23.21-13.46V100.63c0-5.29-2.62-10.14-7.27-12.99z",
    height: 512,
    width: 576,
}


function create_mazes() {
    $(".maze-container").each(function(i, elm){
        create_maze($(elm));
    });
}

function create_maze(container) {
    var x_trans = 10;
    var y_trans = 10;

    function draw_maze(data) {
        var canvas = $("<canvas width=\"500\" height=\"500\">")
        container.append(canvas);
        var cell_width = (canvas.width() - (2 * x_trans) )  / data.width
        var cell_height = (canvas.height() - (2 * y_trans) )  / data.height
        var ctx = canvas.get(0).getContext('2d');
        ctx.lineWidth = 6;
        ctx.lineCap = "square";
        ctx.beginPath();
        ctx.translate(x_trans, y_trans);
        $.each(data.cells, function (i, cell) {
            if (!cell.seen) {
                ctx.fillStyle = 'grey';
                ctx.fillRect(cell.x*cell_width, cell.y*cell_height, cell_width, cell_height);
            }
        });

        function draw_wall(start_x, start_y, end_x, end_y) {
            ctx.moveTo(start_x*cell_width, start_y*cell_height);
            ctx.lineTo(end_x*cell_width, end_y*cell_height);
        }

        function north_wall(cell) {
            draw_wall(cell.x, cell.y, cell.x+1, cell.y)
        }

        function east_wall(cell) {
            draw_wall(cell.x+1, cell.y, cell.x+1, cell.y+1)
        }

        function south_wall(cell) {
            draw_wall(cell.x, cell.y+1, cell.x+1, cell.y+1)
        }

        function west_wall(cell) {
            draw_wall(cell.x, cell.y, cell.x, cell.y+1)
        }

        $.each(data.cells, function (i, cell) {
            if (!cell.seen) {
                if (cell.y == 0) {
                    north_wall(cell);
                }
                if (cell.y == data.height - 1) {
                    south_wall(cell);
                }
                if (cell.x == 0) {
                    west_wall(cell);
                }
                if (cell.x == data.width - 1) {
                    east_wall(cell);
                }
            }
            if (cell.path_north === false) {
                north_wall(cell);
            }
            if (cell.path_east === false) {
                east_wall(cell);
            }
            if (cell.path_south === false) {
                south_wall(cell);
            }
            if (cell.path_west === false) {
                west_wall(cell);
            }
        });
        ctx.stroke();

        // Add current location
        function add_svg(x, y, svg_obj, color, scale_factor) {
            var scale = scale_factor * cell_height / svg_obj.height;
            var domMatrix = new DOMMatrix();
            domMatrix.a = scale;
            domMatrix.d = scale;
            domMatrix.e = ((x + 0.5) * cell_width) - (svg_obj.width * scale / 2);
            domMatrix.f = ((y + 0.5) * cell_height) - (svg_obj.height * scale / 2);
            var p = new Path2D();
            var svg_path = new Path2D(svg_obj.data);
            p.addPath(svg_path, domMatrix)
            ctx.fillStyle = color;
            ctx.fill(p);
        }

        add_svg(data.current_x, data.current_y, WALKING_SVG, "green", 0.75)
        add_svg(data.end_x, data.end_y, BOOK_SVG, "purple", 0.6)

    }

    $.ajax({
        url: container.data("url"),
        success: draw_maze,
        error: function() {alert("Error loading maze. Please try again.")}
    });
}



$(function() {
    create_mazes();
});