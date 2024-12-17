package pyritship;

import burp.api.montoya.intruder.AttackConfiguration;
import burp.api.montoya.intruder.PayloadGenerator;
import burp.api.montoya.intruder.PayloadGeneratorProvider;

public class PyRITShipPayloadGeneratorProvider implements PayloadGeneratorProvider {
    private PyRITShip pyritShip;

    public PyRITShipPayloadGeneratorProvider(PyRITShip pyritShip) {
        this.pyritShip = pyritShip;
    }

    @Override
    public String displayName() {
        return "PyRIT Ship Prompt Generator";
    }

    @Override
    public PayloadGenerator providePayloadGenerator(AttackConfiguration attackConfiguration) {
        return new PyRITShipPayloadGenerator(pyritShip);
    }
}