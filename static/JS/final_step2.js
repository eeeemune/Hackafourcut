function clicked_frame_option(self) {
  $.each($(".frame_option"), function (element) {
    $(".frame_option").removeClass("selected");
  });
  self = $(self);
  self.addClass("selected");

  $(document).ready(function () {
    let frame_name = self.data("frame_name");
    $(".frame_name").val(frame_name);
    $(".frame").attr("src", `../static/img/frames/${frame_name}.png`);
  });
}

function clicked_btn_step2_next(self) {
  $("form").submit();
}
