package pyritship;

import burp.api.montoya.core.Annotations;
import burp.api.montoya.core.HighlightColor;
import burp.api.montoya.core.ToolType;
import burp.api.montoya.http.handler.*;
import burp.api.montoya.logging.Logging;

import static burp.api.montoya.http.handler.RequestToBeSentAction.continueWith;
import static burp.api.montoya.http.handler.ResponseReceivedAction.continueWith;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

import java.util.regex.*;

import org.json.JSONObject;

class PyRITShipHttpHandler implements HttpHandler {
    private Logging logging;
    private PyRITShip pyritShip;
    private HttpClient httpClient;

    public PyRITShipHttpHandler(PyRITShip pyritShip) {
        this.pyritShip = pyritShip;
        this.logging = pyritShip.logging;
    }

    @Override
    public RequestToBeSentAction handleHttpRequestToBeSent(HttpRequestToBeSent requestToBeSent) {

        Annotations annotations = requestToBeSent.annotations();

        // if (requestToBeSent.toolSource().toolType() == ToolType.INTRUDER) {
        //     int messageId = requestToBeSent.messageId();
        // }

        if (requestToBeSent.toolSource().toolType() == ToolType.PROXY && pyritShip.HttpConverterEnabled()) {

            String originalBodyText = requestToBeSent.bodyToString();
            String newBodyText = originalBodyText;

            //[CONVERT]text[/CONVERT]
            Pattern convertPattern = Pattern.compile("\\[CONVERT\\](?<text>.*?)\\[/CONVERT\\]");
            Matcher convertMatcher = convertPattern.matcher(originalBodyText);
            while (convertMatcher.find()) {
                String text = convertMatcher.group("text");

                if (httpClient == null) {
                    httpClient = HttpClient.newHttpClient();
                }

                JSONObject obj = new JSONObject();
                obj.put("text", text);

                String pyritShipURL = pyritShip.PyRITShipURL();
                if (pyritShipURL.endsWith("/")) {
                    pyritShipURL = pyritShipURL.substring(0, pyritShipURL.length() - 1);
                }
                
                URI uri = URI.create(pyritShipURL + "/prompt/convert/" + pyritShip.HttpConverterName());
                HttpRequest request = HttpRequest.newBuilder(uri)
                        .header("Content-Type", "application/json")
                        .method("POST", HttpRequest.BodyPublishers.ofString(obj.toString())).build();

                try {
                    HttpResponse<String> response = this.httpClient.send(request, HttpResponse.BodyHandlers.ofString());

                    int statusCode = response.statusCode();
                    if (statusCode != 200) {
                        logging.logToError("Intruder PyRITShip converter http error " + statusCode);
                        return continueWith(requestToBeSent, annotations);
                    }

                    obj = new JSONObject(response.body());
                    String convertedText = obj.getString("converted_text");

                    newBodyText = newBodyText.replace("[CONVERT]" + text + "[/CONVERT]", convertedText);
                }
                catch(Exception e) {
                    logging.logToError("Error parsing response: " + e.toString());
                    return continueWith(requestToBeSent, annotations);
                }
            }

            return continueWith(requestToBeSent.withBody(newBodyText), annotations);
        }

        return continueWith(requestToBeSent, annotations);
    }

    @Override
    public ResponseReceivedAction handleHttpResponseReceived(HttpResponseReceived responseReceived) {
        
        Annotations annotations = responseReceived.annotations();

        //burp.api.montoya.http.message.requests.HttpRequest initialRequest = responseReceived.initiatingRequest();
        //int messageId = responseReceived.messageId();

        if (responseReceived.toolSource().toolType() == ToolType.INTRUDER) {
            try {

                JSONObject obj = new JSONObject(responseReceived.bodyToString());
                Object result = obj.query(pyritShip.PayloadParse());

                if (httpClient == null) {
                    httpClient = HttpClient.newHttpClient();
                }

                obj = new JSONObject();
                obj.put("scoring_true", pyritShip.ScoringTrue());
                obj.put("scoring_false", pyritShip.ScoringFalse());
                obj.put("prompt_response", result);

                String pyritShipURL = pyritShip.PyRITShipURL();
                if (pyritShipURL.endsWith("/")) {
                    pyritShipURL = pyritShipURL.substring(0, pyritShipURL.length() - 1);
                }
                
                URI uri = URI.create(pyritShipURL + "/prompt/score/" + pyritShip.ScorerName());
                HttpRequest request = HttpRequest.newBuilder(uri)
                        .header("Content-Type", "application/json")
                        .method("POST", HttpRequest.BodyPublishers.ofString(obj.toString())).build();


                HttpResponse<String> response = this.httpClient.send(request, HttpResponse.BodyHandlers.ofString());

                int statusCode = response.statusCode();
                if (statusCode != 200) {
                    logging.logToError("Intruder PyRITShip scoring http error " + statusCode);
                    return continueWith(responseReceived, annotations);
                }

                obj = new JSONObject(response.body());
                String score = obj.getString("scoring_text");

                annotations = annotations.withNotes("Score response: " + score);
                if (score.equals("True")) {
                    PyRITShipPayloadGenerator.scoringGoalAchieved = true;
                    annotations = annotations.withHighlightColor(HighlightColor.GREEN);
                }
            }
            catch(Exception e) {
                logging.logToError("Error parsing response: " + e.toString());
            }
        }

        return continueWith(responseReceived, annotations);
    }
}
