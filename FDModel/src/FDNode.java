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

    public FDNode(double aVal, FDArc anOther, FDNode aNext) {
        this.val=aVal;
        this.other=anOther;
        this.next=aNext;
        this.clean();
    }
    public FDNode(double aVal) {
        this(aVal, null, null);
    }
    public FDNode() {
        this(0.0);
    }
    public void clean() {
        this.newVal=0.0;
        this.oldVal=0.0;
    }
    public FDNode addArc(FDNode aNode, double val) {
        if (this.next != null) {
            return this.next.addArc(aNode, val);
        } else {
            this.next=new FDNode(val, new FDArc(val, aNode), null);
            return this.next;
        }
    }
    public FDNode addArc(double val) {
        return this.addArc(new FDNode(), val);
    }

    public FDNode addArc() {
        return this.addArc(0.0);
    }
}
