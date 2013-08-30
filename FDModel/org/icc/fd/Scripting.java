package org.icc.fd;

import org.mozilla.javascript.*;
import sun.org.mozilla.javascript.Context;

/**
 * Created with IntelliJ IDEA.
 * User: eugeneai
 * Date: 30.08.13
 * Time: 14:23
 * To change this template use File | Settings | File Templates.
 */
public class Scripting {
    public Context context;
    public Scriptable scope;

    Scripting () {
        this.context = Context.enter();
        this.scope = this.context.initStandardObjects();
        //TODO load our context objects as, e.g., a global variale FD, or fd;
    }

    @Override
    protected void finalize() throws Throwable {
        this.context.exit();
        super.finalize();
    }

    public Object evaluateString(String cmd, boolean logging) {
        Object rc = this.context.evaluateString(this.scope, cmd, "<FDModel.JS.context.cmd>", 1, null);
        if (logging) {
            System.out.print(Context.toString(rc));
        }
        return rc;
    }

    public static void main(String [] args) {
        System.out.println("Javascript test.");
    }
}
