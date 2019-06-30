function clientUpdateContent(client_id, content_id) {
    $.ajax({
        type: "POST",
        url: "/clients/update_content_ajax",
        data: {
            client_id: client_id,
            content_id: content_id
        },
        success: function (result) {
            //alert('Updated');
            //window.location.reload();
        },
        error: function (result) {
            alert('Error updating content');
            window.location.reload();
        }
    });
}


$(function() {

  $("#content-picker").on("changed.bs.select", function(e, clickedIndex, newValue, oldValue) {

      clientUpdateContent(this.attributes["data-client"].value, this.value);
      console.log(this.value, clickedIndex, newValue, oldValue)
  });

});