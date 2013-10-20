d3.selectAll('table.klystable tr > td').on("click",function(){
    //d3.select(this).style("color","#468847");
    var elem = d3.select(this);
    if ( elem.classed("text-activated") ) {
        elem.classed("text-activated",false);
        elem.classed("text-faulted",true);
    } else if ( elem.classed("text-faulted") ) {
        elem.classed("text-deactivated",true);
        elem.classed("text-faulted",false);
    } else {
        elem.classed("text-activated",true);
    }
    
    //d3.select(this).classed("text-activated",true); 
});