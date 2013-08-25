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
        FDNode root = M.node, n1, n2;
        root.val=1.0;
        n1 = root.addArc(0.1);
        n2 = root.addArc(0.9);
        n2.addArc(root, 1.0);
        for (int i=1; i<=100; i++) {
            M.step(new EulerIntegrationTechnique(), 0.1);
            System.out.printf("%02d: FDModel.node.val=%f\n", i, M.node.val);
        };
        System.out.println("Ok");
    }
}
