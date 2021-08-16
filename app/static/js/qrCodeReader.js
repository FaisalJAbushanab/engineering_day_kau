var qrcode = window.qrcode;

const video = document.createElement("video");
const canvasElement = document.getElementById("qr-canvas");
const canvas = canvasElement.getContext("2d");

const qrResult = document.getElementById("qr-result");
const outputData = document.getElementById("outputData");
const btnScanQR = document.getElementById("btn-scan-qr");


let scanning = false;

qrcode.callback = res => {
  if (res) {
    // outputData.innerText = res;
    scanning = false;
    if(res.startsWith('checkout/user/')){
      fetch(res).then(res => res.json())
      .then(data => {
        outputData.innerHTML = '';
        outputData.innerHTML += '<p> الاسم الثلاثي: ' + data.full_name + '</p>'; 
        outputData.innerHTML += '<p> البريد الآلكتروني: ' + data.email + '</p>'; 
        outputData.innerHTML += '<p> التخصص: ' + data.field + '</p>';
        outputData.innerHTML += '<p> تاريخ التسجيل: ' + data.created_at + '</p>';
        if(data.roles == 'Admin'){
        outputData.innerHTML += '<p> نوع العضوية: الادارة</p>';
        }else if( data.roles == 'Mod'){
          outputData.innerHTML += '<p> نوع العضوية: منظم</p>';
        }else{
          outputData.innerHTML += '<p> نوع العضوية: الحضور</p>';
        }
        outputData.innerHTML += '<p> <a id="again" class="again"> مسح آخر </a> </p>' ;
        const again = document.getElementById("again");
        again.onclick = () => {
          navigator.mediaDevices
            .getUserMedia({ video: { facingMode: "environment" } })
            .then(function(stream) {
              scanning = true;
              qrResult.hidden = true;
              btnScanQR.hidden = true;
              canvasElement.hidden = false;
              video.setAttribute("playsinline", true); // required to tell iOS safari we don't want fullscreen
              video.srcObject = stream;
              video.play();
              tick();
              scan();
            });
        };
    }
      )  
      .catch(error => console.log('Error'))
    }

    video.srcObject.getTracks().forEach(track => {
      track.stop();
    });

    qrResult.hidden = false;
    canvasElement.hidden = true;
    btnScanQR.hidden = false;
  }
};

window.onload = () => {
  navigator.mediaDevices
    .getUserMedia({ video: { facingMode: "environment" } })
    .then(function(stream) {
      scanning = true;
      qrResult.hidden = true;
      btnScanQR.hidden = true;
      canvasElement.hidden = false;
      video.setAttribute("playsinline", true); // required to tell iOS safari we don't want fullscreen
      video.srcObject = stream;
      video.play();
      tick();
      scan();
    });
};


function tick() {
  canvasElement.height = video.videoHeight;
  canvasElement.width = video.videoWidth;
  canvas.drawImage(video, 0, 0, canvasElement.width, canvasElement.height);

  scanning && requestAnimationFrame(tick);
}

function scan() {
  try {
    qrcode.decode();
  } catch (e) {
    setTimeout(scan, 300);
  }
}
