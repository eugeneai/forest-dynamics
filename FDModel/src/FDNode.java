/**
 * Created with IntelliJ IDEA.
 * User: eugeneai
 * Date: 23.08.13
 * Time: 20:52
 * To change this template use File | Settings | File Templates.
 */
public class FDNode {
    public double val;     // the value
    public double dVal;    // the value's integrated delta on a step
    public boolean marked; // used to mark visited nodes during integration.
    public FDArc siblings;

    public FDNode(double aVal, FDArc siblings) {
        this.val=aVal;
        this.siblings=siblings;
        this.clean();
    }
    public FDNode(double aVal) {
        this(aVal, null);
    }
    public FDNode() {
        this(0.0);
    }
    public void clean() {
        this.dVal = 0.0;
        this.marked = false;
    }
    public FDNode addArc(FDNode aNode, double val) {
        if (this.siblings != null) {
            this.siblings.addArc(val, aNode);
            return aNode;
        } else {
            this.siblings=new FDArc(val, aNode, null);
            return aNode;
        }
    }
    public FDNode addArc(double val) {
        return this.addArc(new FDNode(), val);
    }

    public FDNode addArc() {
        return this.addArc(0.0);
    }
}
