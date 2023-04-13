// start jquery
$(document).ready( 
    //function to call when server is created
    function(){
    $.ajax({
        url: "/createMol",
        type: "GET",
        dataType: "text",
        success: function(data, status, xhr){
            $("#display-container").empty()
            data = data.replace('width="1000"', 'width="500"');
            data = data.replace('height="1000"', 'height="400"');
            data = data.replace('<svg ', '<svg version="1.1" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid meet" ');
            $("#display-container").append(data)
        },
        error: function(xhr, status, error) {
            if (xhr.status === 404) {
                alert("Submission Invalid.");
            } else {
                alert("Error: " + error);
            } 
        }
    });

    $("#rot-x").click(function(){
        var dimension = "x";
        rotate(dimension)
        {
            $.ajax({
                url: "/createMol",
                type: "GET",
                dataType: "text",
                success: function(data, status, xhr){
                    $("#display-container").empty()
                    data = data.replace('width="1000"', 'width="500"');
                    data = data.replace('height="1000"', 'height="400"');
                    data = data.replace('<svg ', '<svg version="1.1" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid meet" ');
                    $("#display-container").append(data)
                }
            });
        }

    }),

    $("#rot-y").click(function(){
        var dimension = "y";
        rotate(dimension)
        {
            $.ajax({
                url: "/createMol",
                type: "GET",
                dataType: "text",
                success: function(data, status, xhr){
                    $("#display-container").empty()
                    data = data.replace('width="1000"', 'width="500"');
                    data = data.replace('height="1000"', 'height="400"');
                    data = data.replace('<svg ', '<svg version="1.1" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid meet" ');
                    $("#display-container").append(data)
                }
            });
        }
    }),
    
    $("#rot-z").click(function(){
        var dimension = "z";
        rotate(dimension)
        {
            $.ajax({
                url: "/createMol",
                type: "GET",
                dataType: "text",
                success: function(data, status, xhr){
                    $("#display-container").empty()
                    data = data.replace('width="1000"', 'width="500"');
                    data = data.replace('height="1000"', 'height="400"');
                    data = data.replace('<svg ', '<svg version="1.1" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid meet" ');
                    $("#display-container").append(data)
                }
            });
        }
    })

    }
)

function rotate(dimension, degree) {
    $.ajax({
        url: '/rotate', 
        type: 'POST',
        data: {
            'dimension': dimension,
            'degree': degree
        },
        success: function (response) {
            console.log("Rotated.");
        },
        error: function (xhr, textStatus, errorThrown) {
            console.log("Rotation Error.");
        }
    });
}
