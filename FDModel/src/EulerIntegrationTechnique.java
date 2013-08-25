/**
 * Created with IntelliJ IDEA.
 * User: eugeneai
 * Date: 25.08.13
 * Time: 11:31
 * To change this template use File | Settings | File Templates.
 */
public class EulerIntegrationTechnique extends FDModel.BaseIntegrationTechnique
        implements FDModel.IntegrationTechnique{
    public int steps;
    public static class EulerAction implements FDModel.Action {
        public void execute(FDNode node, double dt) {
            double dv=0.0, d;
            FDArc arc;
            arc = node.siblings;
            while (arc != null) {
                d = node.val * arc.val * dt;
                dv += d;
                arc.target.dVal += d;
                arc = arc.next;
            }
            node.dVal -= dv;
        }
    }
    public EulerIntegrationTechnique() {
        this(1);
    }
    public EulerIntegrationTechnique(int steps) {
        this.steps=steps;
    }
    public void integrationStep(FDNode node, double dt) {
        EulerAction ea = new EulerAction();
        for (int i=0; i<this.steps; i++) {
            this.nodeExecute(node, ea, dt);
        }
    }
}