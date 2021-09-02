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
            if (!cell.path_north) {
                ctx.moveTo(cell.x*cell_width, cell.y*cell_height);
                ctx.lineTo((cell.x+1)*cell_width, cell.y*cell_height);
            }
            if (!cell.path_east) {
                ctx.moveTo((cell.x+1)*cell_width, cell.y*cell_height);
                ctx.lineTo((cell.x+1)*cell_width, (cell.y + 1)*cell_height);
            }
            if (!cell.path_south) {
                ctx.moveTo(cell.x*cell_width, (cell.y+1)*cell_height);
                ctx.lineTo((cell.x+1)*cell_width, (cell.y+1)*cell_height);

            }
            if (!cell.path_west) {
                ctx.moveTo(cell.x*cell_width, cell.y*cell_height);
                ctx.lineTo(cell.x*cell_width, (cell.y + 1)*cell_height);
            }
            ctx.stroke();
            ctx.save();
        });

        // TODO replace with person
        ctx.beginPath();
        var x = (data.current_x + 0.5) * cell_width;
        var y = (data.current_y + 0.5) * cell_height;
        var radius = cell_width / 4

        ctx.arc(x, y, radius, 0, Math.PI * 2, true)
        ctx.fillStyle = "red";
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