function filtra(col,vl) {
  var filter, table, tr, td, i;
  filter = vl.toUpperCase();
  table = document.getElementById("tbfiltro");
  tr = table.getElementsByTagName("tr");
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[col];
    if (td) {
      if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }       
  }
}

function opcoes(pg,dv,data){
  $.ajax({
    url:pg, 
    type:'post', 
    data:data, 
    success: function(retorno){
      $("#" + dv).html(retorno);
    }//,
    // beforeSend : function(){
    //   $("#" + dv).html("Carregando...");
    // }
  })
}


function open_menu() {
  var x = document.getElementById("dv_menu");
  if (x.className === "menu") {
    x.className += " responsive";
  } else {
    x.className = "menu";
  }
}