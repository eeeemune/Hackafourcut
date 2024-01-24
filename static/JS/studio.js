function data_url_of(canvas) {
  return canvas.toDataURL("image/jpeg");
}

function snap_photo() {
  html2canvas(document.querySelector("#video_container")).then((canvas) => {
    $(".snap_cnt").val(parseInt($(".snap_cnt").val()) + 1);
    $(".gogo_url").val(data_url_of(canvas));
    $("form").submit();
  });
}

function write_left_time() {
  snap_cnt = $(".snap_cnt");
  let gogo_cnt_down = setInterval(function () {
    let now_cnt_obj = $(".count_down .cnt_img");
    let now_cnt = now_cnt_obj.attr("data-cnt");
    let now_cnt_img = $(".count_down img");
    if (0 < now_cnt) {
      now_cnt_obj.attr("data-cnt", now_cnt - 1);
      now_cnt_img.attr("src", `../static/img/cnt_${now_cnt}.png`);
    } else {
      clearInterval(gogo_cnt_down);
      snap_photo();
    }
  }, 1000);
}

function enableMedia() {
  var video = document.getElementById("video_element");

  navigator.getUserMedia =
    navigator.mediaDevices.getUserMedia ||
    navigator.getUserMedia ||
    navigator.webkitGetUserMedia ||
    navigator.mozGetUserMedia ||
    navigator.msGetUserMedia;

  if (navigator.getUserMedia) {
    navigator.mediaDevices
      .getUserMedia({ audio: false, video: { facingMode: "user" } })
      .then(function (stream) {
        video.srcObject = stream;
        video.onloadedmetadata = function (e) {
          video.play();
        };
      })
      .catch(function (e) {
        console.log("error: " + e);
      });
  } else {
    console.log("getUserMedia() not available.");
    video.src = "somevideo.webm"; // fallback.
  }
}
$(document).ready(function () {
  enableMedia();
  write_left_time();
});
