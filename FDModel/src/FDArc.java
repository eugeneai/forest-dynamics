/**
 * Created with IntelliJ IDEA.
 * User: eugeneai
 * Date: 24.08.13
 * Time: 9:55
 * To change this template use File | Settings | File Templates.
 */
public class FDArc {
    public double val;
    public FDNode target;
    public FDArc (double aVal, FDNode aTarget) {
        this.target = aTarget;
        this.val = aVal;
    }
    public FDArc (double aVal) {
        this(aVal, new FDNode());
    }
}
