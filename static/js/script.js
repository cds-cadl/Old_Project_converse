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

        const latency = (new Date() - startTime) / 1000;

        $.post('/log', { time: time, latency: latency, action: action, prompt: input_text, resp1: data.resp, resp2: data.alt_resp }, function () {
          console.log("Data logged successfully!");
        }, 'json');

      }, 'json');

    }
  });
});


// Text-to-speech buttons

$(document).ready(function () {
  $(document).keydown(function (event) {
    if (event.key === '1' && !$('#num-prompts').is(':focus')) {
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
    if (event.key === '2' && !$('#num-prompts').is(':focus')) {
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

// To track the prompt number
var promptNum = 0;
var maxPrompt = 0;
var startTrainer;

// File Upload
$(document).ready(function () {
  // File input change event
  $('#file-input').on('change', function () {
    var filename = $(this).val().split('\\').pop();
    $('#filename').val(filename);
  });

  // Filename input keydown event
  $('#filename').on('keydown', function (event) {
    if (event.key === 'Backspace') {
      $('#file-input').val('');
      $(this).val('');
    }
    event.preventDefault();
  });

  // Upload button click event
  $('#upload-button').on('click', function (event) {
    event.preventDefault(); 
    var file = $('#file-input').prop('files')[0];

    promptNum = 0;
    maxPrompt = 0;

    if (file) {
      var numPrompts = parseInt($('#num-prompts').val());
      if (!numPrompts) {
        numPrompts = -1;
      }

      var formData = new FormData();
      formData.append('file', file);
      formData.append('num_lines', numPrompts);

      $.ajax({
        url: '/upload',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
          if (response.code == 200) {
            promptNum = 1;
            maxPrompt = response.numPrompts;
          }
          alert(response.msg);
        }
      });
    }

    else {
      alert('Please select a file.');
    }
    // Reset form values
    $('#file-input').val('');
    $('#filename').val('');
    $('#num-prompts').val('');
    $('#trainerPrompt').val('');
  });
});



// for scoring, not in use right now:
var trainerPrompt = "";
// var trainerResponse = "";

// To generate prompt for trainer
$(document).ready(function () {
  $('#trainerGenerate').click(function () {
    if (promptNum != 0) {
      if (promptNum > maxPrompt) {
        $('#trainerPrompt').val("Completed! A log has been created!");
        trainerPrompt='';
      }
      else {
        $.ajax({
          url: '/generate-sentence',
          type: 'POST',
          data: { line: promptNum },
          success: function (response) {
            trainerPrompt = response;
            $('#trainerPrompt').val('Say "' + response + '"');
          }
        });
        promptNum += 1;
        startTrainer = new Date();
      }
    }
  });
});

$(document).ready(function (){
  $('#logTrainer').click(function () {
    if (promptNum != 0 && !$('#trainerPrompt').val().includes("Completed!")){
      var hours = startTrainer.getHours().toString().padStart(2, '0');
      var minutes = startTrainer.getMinutes().toString().padStart(2, '0');
      var seconds = startTrainer.getSeconds().toString().padStart(2, '0');
      var time = hours + ':' + minutes + ':' + seconds;

      var latency = (new Date() - startTrainer) / 1000;

      $.post('/log-trainer', { prompt:trainerPrompt, latency:latency, time:time}, function () {
        console.log("Data Logged Successfully!");
        console.log(trainerPrompt);
        trainerPrompt = "";
      }, 'json');
    }
  });
});


/*
// To score user's response
// Not usable right now since trainer is not connected to OSDPI

$(document).ready(function () {

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
*/

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
