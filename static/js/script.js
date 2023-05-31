/*
***********
QUICKTALKER
***********
*/

var startTime;
var action;

// Capture the typing start time
$(document).ready(function () {
  $('#prompt').on('input', function () {
    startTime = new Date();
    action = "TEXT";
  });
});


// Voice Recorder

let mediaRecorder;
let chunks = [];
let recording = false;

const startRecording = async () => {
  if (!recording) {
    startTime = new Date();  // Capture the start time when recording starts
    action = "AUDIO";
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();
    recording = true;

    mediaRecorder.addEventListener("dataavailable", function (event) {
      chunks.push(event.data);
    });
  }
};

const stopRecording = () => {
  mediaRecorder.stop();
  recording = false;

  mediaRecorder.addEventListener("stop", async () => {
    const blob = new Blob(chunks, { type: "audio/wav" });
    chunks = [];

    const formData = new FormData();
    formData.append("audio", blob, "request.wav");

    const response = await fetch("/save-audio", {
      method: "POST",
      body: formData,
    });

    const transcriptionResponse = await fetch("/transcribe", {
      method: "POST",
      body: JSON.stringify({ filename: "request.wav" }),
      headers: {
        "Content-Type": "application/json",
      },
    });

    const transcription = await transcriptionResponse.text();
    document.getElementById("prompt").value = transcription;
  });
};

const clearInputs = () => {
  document.getElementById('prompt').value = '';
  document.getElementById('promptOutput').value = '';
  document.getElementById('promptOutput').setAttribute("rows", "2");
  document.getElementById('promptOutput').style.height = "auto";
  document.getElementById('promptOutput2').value = '';
  document.getElementById('promptOutput2').setAttribute("rows", "2");
  document.getElementById('promptOutput2').style.height = "auto";
}

window.onload = function () {
  document.addEventListener('keydown', (event) => {
    if (!document.getElementById('prompt').matches(':focus')) {
      if (event.key === 'r') {
        startRecording();
        event.preventDefault();
      } else if (event.key === 's') {
        stopRecording();
        event.preventDefault();
      } else if (event.key === 'c') {
        clearInputs();
        event.preventDefault();
      }
    }
  });
}

// AI Generated Response

$(document).ready(function () {
  $(document).keydown(function (event) {

    var input_text = $('#prompt').val();
    if (event.key === 'Enter' && input_text.length !== 0) {
      event.preventDefault();
      $('#prompt').blur();

      $.post('/prompt', { input_text: input_text }, function (data) {
        $('#promptOutput').val(data.resp);
        $('#promptOutput2').val(data.alt_resp);

        var textarea = $('#promptOutput');
        var contentHeight = textarea[0].scrollHeight - parseFloat(textarea.css('padding-top')) - parseFloat(textarea.css('padding-bottom'));
        textarea.height(contentHeight);

        var textarea = $('#promptOutput2');
        var contentHeight = textarea[0].scrollHeight - parseFloat(textarea.css('padding-top')) - parseFloat(textarea.css('padding-bottom'));
        textarea.height(contentHeight);

        // For logging:
        var hours = startTime.getHours().toString().padStart(2, '0');
        var minutes = startTime.getMinutes().toString().padStart(2, '0');
        var seconds = startTime.getSeconds().toString().padStart(2, '0');
        var time = hours + ':' + minutes + ':' + seconds;

        latency = (new Date() - startTime) / 1000

        $.post('/log', { time: time, latency: latency, action: action, prompt: input_text, resp1: data.resp, resp2: data.alt_resp }, function () {
          console.log("Data logged successfully!")
        }, 'json');

      }, 'json');

    }
  });
});


// Text-to-speech buttons

$(document).ready(function () {
  $(document).keydown(function (event) {
    if (event.key === '1') {
      event.preventDefault();
      var inputText = $('#promptOutput').val();
      if (inputText) {
        $.post('/text-to-speech', { input_text: inputText }, function (data) {
          var audio = new Audio('data:audio/mp3;base64,' + data.audio_content);
          audio.play();
        }, 'json');
      }
    }
  });
});

$(document).ready(function () {
  $(document).keydown(function (event) {
    if (event.key === '2') {
      var inputText = $('#promptOutput2').val();
      if (inputText) {
        $.post('/text-to-speech', { input_text: inputText }, function (data) {
          var audio = new Audio('data:audio/mp3;base64,' + data.audio_content);
          audio.play();
        }, 'json');
        event.preventDefault();
      }
    }
  });
});

/*
*******
TRAINER
*******
*/
var trainerPrompt = "";
var trainerResponse = "";

$(document).ready(function () {
  $('#trainerPromptOut').click(function () {
    $.ajax({
      url: '/generate-sentence',
      type: 'POST',
      success: function (response) {
        trainerPrompt = response;
        $('#trainerPrompt').val('Say "' + response + '"');
      }
    });
  });
});

$(document).ready(function () {
  
    $('#I').click(function () {
      if (trainerPrompt) {
      trainerResponse += "I ";
      }
    });

    $('#agree').click(function () {
      if (trainerPrompt) {
      trainerResponse += "agree ";
      }
    });

    $('#disagree').click(function () {
      if (trainerPrompt) {
      trainerResponse += "disagree ";
      }
    });
    
    $('#score').click(function () {
      if (trainerResponse) {
        $.ajax({
          url: '/score',
          type: 'POST',
          data: { prompt: trainerPrompt, resp: trainerResponse },
          success: function (response) {
            $('#scoreOut').text("Score: " + response);
            trainerPrompt = "";
            trainerResponse = "";
          }
        });
      }
    });
});


/*
*******
CHATBOT
*******
*/

// Change symbol: record to send (while typing)
const chatInput = document.getElementById('chat-input');
const recordButton = document.getElementById('chat-record');

chatInput.addEventListener('input', function () {
  if (chatInput.value.trim() !== '') {
    recordButton.innerHTML = '<i class="fa-xl fa-solid fa-paper-plane"></i>';
    recordButton.setAttribute('title', 'Send');
  } else {
    recordButton.innerHTML = '<i class="fa-xl fa-solid fa-microphone"></i>';
    recordButton.setAttribute('title', 'Record');
  }
});
