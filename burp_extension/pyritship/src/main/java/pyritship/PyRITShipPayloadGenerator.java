package pyritship;

import burp.api.montoya.intruder.GeneratedPayload;
import burp.api.montoya.intruder.IntruderInsertionPoint;
import burp.api.montoya.intruder.PayloadGenerator;
import burp.api.montoya.logging.Logging;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

//import org.json.JSONArray;
import org.json.JSONObject;

public class PyRITShipPayloadGenerator implements PayloadGenerator {
    private int payloadTries = 0;
    private int payloadMaxTries = 0;
    private HttpClient httpClient;
    private Logging logging;
    private String pyritShipURL;
    private String intruderGoal;
    public static boolean scoringGoalAchieved = false;

    PyRITShipPayloadGenerator(PyRITShip pyritShip) {
        this.logging = pyritShip.logging;
        this.pyritShipURL = pyritShip.PyRITShipURL();
        if (this.pyritShipURL.endsWith("/")) {
            this.pyritShipURL = this.pyritShipURL.substring(0, this.pyritShipURL.length() - 1);
        }
        this.intruderGoal = pyritShip.IntruderGoal();

        this.httpClient = HttpClient.newHttpClient();

        this.payloadMaxTries = pyritShip.MaxTries();

        scoringGoalAchieved = false;
    }

    @Override
    public GeneratedPayload generatePayloadFor(IntruderInsertionPoint insertionPoint) {
        payloadTries++;

        if (payloadTries > payloadMaxTries || scoringGoalAchieved) {
            return GeneratedPayload.end();
        }

        String prompt = "";
        try {
            logging.logToOutput("Payload " + payloadTries);

            JSONObject obj = new JSONObject();
            obj.put("prompt_goal", intruderGoal);
            //obj.put("previous", array);

            URI uri = URI.create(pyritShipURL + "/prompt/generate");
            HttpRequest request = HttpRequest.newBuilder(uri)
                    .header("Content-Type", "application/json")
                    .method("POST", HttpRequest.BodyPublishers.ofString(obj.toString()))
                    .build();
            HttpResponse<String> response = this.httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            int statusCode = response.statusCode();
            if (statusCode != 200) {
                logging.logToError("Intruder PyRITShip get prompt http error " + statusCode);
                return GeneratedPayload.end();
            }

            obj = new JSONObject(response.body());
            prompt = obj.getString("prompt");
        } catch (Exception e) {
            logging.logToError("Intruder PyRITShip get prompt error " + e.toString());
            return GeneratedPayload.end();
        }

        GeneratedPayload payload = GeneratedPayload.payload(prompt);
        return payload;
    }
}
