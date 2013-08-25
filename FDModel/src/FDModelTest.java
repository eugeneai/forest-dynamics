/**
 * Created with IntelliJ IDEA.
 * User: eugeneai
 * Date: 24.08.13
 * Time: 9:59
 * To change this template use File | Settings | File Templates.
 */
public class FDModelTest {
    public static void main (String [] args) {
        System.out.println("Test of the FDModel suite");
        FDModel M;
        M = new FDModel();
        FDNode root = M.node;
        root.val=1.0;
        root.addArc(0.1);
        root.addArc(0.9);
        M.step(new EulerIntegrationTechnique(), 1);
        System.out.printf("FDModel.node.val=%f\n", M.node.val);
        System.out.println("Ok");
    }
}
