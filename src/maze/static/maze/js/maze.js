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
                return true;
            }
            if (!cell.path_north) {
                north_wall(cell);
            }
            if (!cell.path_east) {
                east_wall(cell);
            }
            if (!cell.path_south) {
                south_wall(cell);
            }
            if (!cell.path_west) {
                west_wall(cell);
            }
        });
        ctx.stroke();

        // TODO replace with person
        ctx.beginPath();
        var x = (data.current_x + 0.5) * cell_width;
        var y = (data.current_y + 0.5) * cell_height;
        var radius = cell_width / 4
        ctx.arc(x, y, radius, 0, Math.PI * 2, true)
        ctx.fillStyle = "red";
        ctx.fill();

        // TODO replace with end (book/door)
        ctx.beginPath();
        var x = (data.end_x + 0.5) * cell_width;
        var y = (data.end_y + 0.5) * cell_height;
        var radius = cell_width / 4
        ctx.arc(x, y, radius, 0, Math.PI * 2, true)
        ctx.fillStyle = "purple";
        ctx.fill();
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