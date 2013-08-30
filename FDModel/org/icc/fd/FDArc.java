package org.icc.fd;

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
    public FDArc next;
    public FDArc (double aVal, FDNode aTarget, FDArc aNext) {
        this.target = aTarget;
        this.val = aVal;
        this.next = aNext;
    }
    public FDArc (double aVal) {
        this(aVal, new FDNode(), null);
    }

    public FDNode addArc(double val, FDNode target) {
        if (this.next != null) {
            return this.next.addArc(val, target);
        } else {
            this.next = new FDArc(val, target, null);
            return target;
        }
    }
}
