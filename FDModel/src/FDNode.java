/**
 * Created with IntelliJ IDEA.
 * User: eugeneai
 * Date: 23.08.13
 * Time: 20:52
 * To change this template use File | Settings | File Templates.
 */
public class FDNode {
    public double val;
    public double newVal;
    public double oldVal;
    public FDArc other;
    public FDNode next;

    FDNode(double aVal) {
        this.val=aVal;
        this.clean();
    }
    public void clean() {
        this.newVal=0.0;
        this.oldVal=0.0;
    }
}
