$(document).ready(function(){
    
    // Load gridster options.
    $(function(){ 
        $(".gridster ul").gridster({
           widget_margins: [20, 20],
           widget_base_dimensions: [100, 100],
           resize: {
              enabled: true
           },
           draggable: {
              handle: '.w_toolbar'
           }
        });
    
        var gridster = $(".gridster ul").gridster().data('gridster');
    
        $('body').on( "click", ".gridster ul > li .fa-times", function() {
          gridster.remove_widget($(this).closest('li'));
        });
    });
    
    // Add Chart Widget.
    function Chart(data, choice, orientacion, color, valor, type){
        // Add gridster tile.
        var gridster = $(".gridster ul").gridster().data('gridster');
        var uid = "id" + Math.random().toString(10).slice(2)
        gridster.add_widget.apply(gridster, ["<li" +
                "><div class='w_toolbar'>" +
                "<span>" + choice + "</span>" +
                "<i class='fa fa-table fa-lg' aria-hidden='true'></i>" + 
                "<i class='fa fa-times fa-lg' aria-hidden='true'></i>" +
                "<i class='fa fa-cog fa-lg' aria-hidden='true' data-toggle='modal' data-target='#myModal'></i>" +
                "</div><div class='w_content' id=" + uid + "></div></li>", 5, 3]);
    
        // Create svg element.
        var svg = dimple.newSvg("#" + uid, "100%", "100%");
        
        // Begin DimpleJS chart creation.
        var myChart = new dimple.chart(svg, data.slice(0,10));
        myChart.setBounds(10, 10, 450, 200);
    
        // If data is fecha, use TimeAxis. Else user CategoricalAxis.
        if (data == "fecha"){
            myChart.addTimeAxis("x", "fecha", "%Y-%m-%d", "%d-%m-%Y");
            myChart.addMeasureAxis("y", valor);
        } else {
             if (orientacion == "Horizontal"){
                 var x = myChart.addMeasureAxis("x", valor);
                 var y = myChart.addCategoryAxis("y", choice);
                 y.addOrderRule(valor, false)
             } else{
                 var x = myChart.addMeasureAxis("y", valor);
                 var y = myChart.addCategoryAxis("x", choice);
                 x.addOrderRule(valor, false)
             }
        }
    
        myChart.height = 200;
        myChart.addSeries(null, type);
    
        myChart.defaultColors = [
            new dimple.color(color, opacity=0.5) 
        ];
    
        myChart.draw(1000);
    
        myChart.svg.attr("viewBox", "0 0 500 300")
            .attr("width", "100%")
            .attr("preserveAspectRatio", "xMaxYMin meet");
    
        // Generate Table.
        var dataTable = tabulate(data, uid, [choice, 'cantidad', 'porcentaje']);
        
        // uppercase the column headers
        dataTable.selectAll("thead th")
            .text(function(column) {
                return column.charAt(0).toUpperCase() + column.substr(1);
            });
            
        // sort by age
        dataTable.selectAll("tbody tr")
            .sort(function(a, b) {
                return d3.descending(a.cantidad, b.cantidad);
            });
        $('#' + uid + "-table").hide()
        
    };
    
    // Add Chart Widget button.
    $("#crear-widget").click(function () {
        var w_data = eval($('.widget-data:selected').text());
        var w_choice = $('.widget-data:selected').text();
        var w_orientacion= $('.orientacion:selected').text();
        var w_color= $('.color:selected').val();
        var w_valor= $('.valor:selected').val();
        var w_type= eval($('.w_type:selected').val());
    
        Chart(w_data, w_choice, w_orientacion, w_color, w_valor, w_type);
    });
    
    // Modify Chart Widget.
    function modifyChart(uid, data, choice, orientacion, color, valor, type){
    
        // Create svg element.
        var svg = dimple.newSvg("#" + uid, "100%", "100%");
        
        // Begin DimpleJS chart creation.
        var myChart = new dimple.chart(svg, data.slice(0,10));
        myChart.setBounds(10, 10, 450, 200);
    
        // If data is fecha, use TimeAxis. Else user CategoricalAxis.
        if (data == "fecha"){
            myChart.addTimeAxis("x", "fecha", "%Y-%m-%d", "%d-%m-%Y");
            myChart.addMeasureAxis("y", valor);
        } else {
             if (orientacion == "Horizontal"){
                 var x = myChart.addMeasureAxis("x", valor);
                 var y = myChart.addCategoryAxis("y", choice);
                 y.addOrderRule(valor, false)
             } else{
                 var x = myChart.addMeasureAxis("y", valor);
                 var y = myChart.addCategoryAxis("x", choice);
                 x.addOrderRule(valor, false)
             }
        }
    
        myChart.height = 200;
        myChart.addSeries(null, type);
    
        myChart.defaultColors = [
            new dimple.color(color, opacity=0.5) 
        ];
    
        myChart.draw(1000);
    
        myChart.svg.attr("viewBox", "0 0 500 300")
            .attr("width", "100%")
            .attr("preserveAspectRatio", "xMaxYMin meet");
    };
    
    // Modify Chart Widget button.
    $("#modificar-widget").click(function () {
    
        var uid = $(this).closest('.modal-body').parent('.modal-content').attr('id')
        $('#' + uid).find('svg').remove();
    
    
        var w_data = eval($('.widget-data:selected').text());
        var w_choice = $('.widget-data:selected').text();
        var w_orientacion= $('.orientacion:selected').text();
        var w_color= $('.color:selected').val();
        var w_valor= $('.valor:selected').val();
        var w_type= eval($('.w_type:selected').val());
    
        modifyChart(uid, w_data, w_choice, w_orientacion, w_color, w_valor, w_type);
    });
    
    
    // This load the actions for the widgets toolbar.
    $(document).on('mouseover mouseout', '.w_toolbar', function(){  
    
         // Pass the widget id to the modal window in order to use it on the
         // modifyChart function. 
         $(".fa-cog").click(function () {
                 var uid = $(this).closest('li').children('.w_content').attr('id');
                 $('.modal-content').attr('id', uid);
         }); 
    
        // Toggle table / chart.
        $(".fa-table").click(function () {
            $(this).closest('li').find('svg').toggle();
            $(this).closest('li').find('table').toggle();
            $(this).closest('li').children('.w_content').css('overflowY', 'scroll');
            $(this).closest('li').children('.w_content').css('overflowX', 'hidden');
        });
    });
    
    // Tabulate chart data.
    function tabulate(data, uid,  columns) {
        var table = d3.select("#" + uid).append("table")
            .attr('class', 'table table-hover')
            .attr('id', uid + "-table"),
            thead = table.append("thead"),
            tbody = table.append("tbody");
    
        // append the header row
        thead.append("tr")
            .selectAll("th")
            .data(columns)
            .enter()
            .append("th")
                .text(function(column) { return column; });
    
        // create a row for each object in the data
        var rows = tbody.selectAll("tr")
            .data(data)
            .enter()
            .append("tr");
    
        // create a cell in each row for each column
        var cells = rows.selectAll("td")
            .data(function(row) {
                return columns.map(function(column) {
                    return {column: column, value: row[column]};
                });
            })
            .enter()
            .append("td")
                .text(function(d) { return d.value; });
        
        return table;
    };

});
