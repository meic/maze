function create_mazes() {
    $(".maze-container").each(function(i, elm){
        create_maze($(elm));
    });
}

function create_maze(container) {
    function draw_maze(data) {
        var cells = {};
        $.each(data.cells, function (i, cell) {
            cells[cell.x + "_" + cell.y] = cell;
        });
        var width_p = 100/(data.width + 2);
        var height_p = 100/(data.height + 2);

        var table = $("<table>")
        for (let y = -1; y < data.height + 1; y++) {
            var maze_row = $("<tr>")
                .addClass("maze-row")
                .css("height", height_p+"%");
            for (let x = -1; x < data.width + 1; x++) {
                cell = cells[x + "_" + y]
                var cell_div = $("<td>")
                    .addClass("maze-cell")
                    .css("width", width_p+"%");

                if (y == -1) {
                    if ( x != -1 && x !=  data.width) {
                        cell_div.addClass("maze-border-bottom")
                    }
                }
                if (y == data.height) {
                    if ( x != -1 && x !=  data.width) {
                        cell_div.addClass("maze-border-top")
                    }
                }
                if (x == -1) {
                    if ( y != -1 && y !=  data.height) {
                        cell_div.addClass("maze-border-right")
                    }
                }
                if (x == data.width) {
                    if ( y != -1 && y !=  data.height) {
                        cell_div.addClass("maze-border-left")
                    }
                }

                if (typeof cell !== "undefined") {
                    cell_div
                        .data("x", cell.x)
                        .data("y", cell.y);
                    if (!cell.path_north){
                        cell_div.addClass("maze-border-top");
                    }
                    if (!cell.path_south){
                        cell_div.addClass("maze-border-bottom");
                    }
                    if (!cell.path_east){
                        cell_div.addClass("maze-border-right");
                    }
                    if (!cell.path_west){
                        cell_div.addClass("maze-border-left");
                    }
                    if (cell.x == data.current_x && cell.y == data.current_y) {
                        cell_div.addClass("current-cell")
                            .html("<i class=\"fas fa-walking\"></i>");
                    }
                }
                maze_row.append(cell_div);
            }
            table.append(maze_row);
        }
        container.append(table);
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