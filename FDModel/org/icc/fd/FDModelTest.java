package org.icc.fd;
/**
 * Created with IntelliJ IDEA.
 * User: eugeneai
 * Date: 24.08.13
 * Time: 9:59
 * To change this template use File | Settings | File Templates.
 */
public class FDModelTest {
    public static FDModel test_one () {
        System.out.println("Test of the FDModel suite");
        FDModel M;
        M = new FDModel();
        FDNode root = M.node, n1, n2;
        root.val=1.0;
        n1 = root.addArc(0.1);
        n2 = root.addArc(0.2);
        n2.addArc(root, 1.0);
        //M.define(n1, "N_1");
        //M.define(n2, "N_2");
        //M.define(M.node, "R");
        int s = M.simulate(new EulerIntegrationTechnique(),55, 100);
        System.out.printf("Steps done: %d\n", s);
        System.out.println("Ok");
        return M;
    }
}
