function clicked_img(self) {
  self = $(self);
  if ($(".selected").length == 4 && !self.hasClass("selected")) {
    return alert("사진은 최대 4개까지 선택 가능합니다.");
  }

  self.hasClass("selected")
    ? self.removeClass("selected")
    : self.addClass("selected");
  idxes = $.map($(".selected"), (element) => $(element).data("idx"));
  $(".selected_img_idxes").val(idxes);
}

function clicked_btn_step1_next(self) {
  if ($(".selected").length != 4) {
    return alert("사진 4장을 선택하세요.");
  }

  $("form").submit();
}
