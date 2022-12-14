<!DOCTYPE html>
<html lang="en-us">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Unity WebGL Player | StreamTheDots</title>
    <link rel="shortcut icon" href="TemplateData/favicon.ico">
    <link rel="stylesheet" href="TemplateData/style.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js"></script>
    <script src="unity-webview.js"></script>
  </head>
  <body>
  <!-- TODO: add a date or something like that like "state"-->
    <a id="connectToTwitch" href="https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=r4htw0tkj8vjq4gaqod6dgmz8apuw1&redirect_uri=https%3a%2f%2fjuansturla.itch.io%2fconnectthedots&scope=channel%3Amanage%3Apolls+channel%3Aread%3Apolls"
    >Connect</a>
    <div id="unity-container" class="unity-desktop">
      <canvas id="unity-canvas"></canvas>
      <div id="unity-loading-bar">
        <div id="unity-logo"></div>
        <div id="unity-progress-bar-empty">
          <div id="unity-progress-bar-full"></div>
        </div>
      </div>
      <div id="unity-footer">
        <div id="unity-webgl-logo"></div>
        <div id="unity-fullscreen-button"></div>
        <div id="unity-build-title">StreamTheDots</div>
      </div>
    </div>
    <script>

<!-- Checkear si tengo un access_token -->
      const queryString = window.location.hash;
      console.log(queryString);
      const queryString2 = queryString.replace('#','?');
      const urlParams = new URLSearchParams(queryString2);
      if(urlParams.has('access_token'))
      {
        const access_token = urlParams.get('access_token');
        console.log(access_token);
        var connectToTwitchButton = document.getElementById('connectToTwitch');
        connectToTwitchButton.style.visibility = "hidden";
      }

      <!-- Podria checkear si tengo un auth_error o algo asi -->

      var buildUrl = "Build";
      var loaderUrl = buildUrl + "/WebGL.loader.js";
      var config = {
        dataUrl: buildUrl + "/WebGL.data",
        frameworkUrl: buildUrl + "/WebGL.framework.js",
        codeUrl: buildUrl + "/WebGL.wasm",
        streamingAssetsUrl: "StreamingAssets",
        companyName: "DefaultCompany",
        productName: "StreamTheDots",
        productVersion: "1.0",
      };

      var container = document.querySelector("#unity-container");
      var canvas = document.querySelector("#unity-canvas");
      var loadingBar = document.querySelector("#unity-loading-bar");
      var progressBarFull = document.querySelector("#unity-progress-bar-full");
      var fullscreenButton = document.querySelector("#unity-fullscreen-button");
      var width0 = "960px";
      var height0 = "600px";

      if (/iPhone|iPad|iPod|Android/i.test(navigator.userAgent)) {
        container.className = "unity-mobile";
        config.devicePixelRatio = 1;
      } else {
        canvas.style.width = "960px";
        canvas.style.height = "600px";
      }
      loadingBar.style.display = "block";

      document.addEventListener(
        'fullscreenchange',
        function() {
          var p = document.getElementById('unity-container');
          var c = document.getElementById('unity-canvas');
          if (document.fullscreenElement) {
            width0 = c.style.width;
            height0 = c.style.height;
            setTimeout(
              function() {
                c.style.width = getComputedStyle(p).width;
                c.style.height = getComputedStyle(p).height;
              },
              250);
          } else {
            c.style.width = width0;
            c.style.height = height0;
          }
        });
      var script = document.createElement("script");
      script.src = loaderUrl;
      script.onload = () => {
        createUnityInstance(canvas, config, (progress) => {
          progressBarFull.style.width = 100 * progress + "%";
        }).then((unityInstance) => {
          window.unityInstance = unityInstance;
          loadingBar.style.display = "none";
          fullscreenButton.onclick = () => {
            var p = document.getElementById('unity-container');
            var c = document.getElementById('unity-canvas');
            c.requestFullscreen = () => {
              p.requestFullscreen();
            };
            unityInstance.SetFullscreen(1);
          };
        }).catch((message) => {
          alert(message);
        });
      };
      document.body.appendChild(script);
    </script>
  </body>
</html>
