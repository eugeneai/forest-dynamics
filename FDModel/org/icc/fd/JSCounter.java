package org.icc.fd;

import sun.org.mozilla.javascript.ScriptableObject;

/**
 * Created with IntelliJ IDEA.
 * User: eugeneai
 * Date: 31.08.13
 * Time: 10:21
 * To change this template use File | Settings | File Templates.
 */
public class JSCounter extends ScriptableObject {
    private static final long serialVersionUID = 438270524527335642L;

    // The zero-argument constructor used by Rhino runtime to create instances
    public JSCounter() {
    }

    // Method jsConstructor defines the JavaScript constructor
    public void jsConstructor(int a) {
        count = a;
    }

    // The class name is defined by the getClassName method
    @Override
    public String getClassName() {
        return "Counter";
    }

    // The method jsGet_count defines the count property.
    public int jsGet_count() {
        return count++;
    }

    // Methods can be defined using the jsFunction_ prefix. Here we define
    //  resetCount for JavaScript.
    public void jsFunction_resetCount() {
        count = 0;
    }

    private int count;
}

