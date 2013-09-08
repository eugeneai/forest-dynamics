#include <stdio.h>
#include <Python.h>
#include <string.h>

typedef struct _PyDMI PyDMI; 	// DynamicModelItem
	
struct _PyDMI {
	PyObject_HEAD
	PyDMI * next;	// next in whole 
	double init_value;
	double value;
	double new_value;
	PyDMI * another;		// links to nodes/edges of inverse type
};

staticforward PyTypeObject PyDMI_Type;

#define PyDMI_Check(v)	((v)->ob_type == &PyDMI_Type)

// The module itself

static PyObject *ErrorObject;
static PyDMI *Head=NULL;

#define BLOCK_SIZE	1000	/* 1K less typical malloc overhead */
#define BHEAD_SIZE	8	/* Enough for a 64-bit pointer */
#define N_INTOBJECTS	((BLOCK_SIZE - BHEAD_SIZE) / sizeof(PyDMI))

struct _dmiblock {
	struct _dmiblock *next;
	PyDMI objects[N_INTOBJECTS];
};

typedef struct _dmiblock PyDMIBlock;

static PyDMIBlock *block_list = NULL;
static PyDMI *free_list = NULL;

static PyDMI *
fill_free_list(void)
{
	PyDMI *p, *q;
	/* XXX Int blocks escape the object heap. Use PyObject_MALLOC ??? */
	p = (PyDMI *) PyMem_MALLOC(sizeof(PyDMIBlock));
	
	if (p == NULL)
		return (PyDMI *) PyErr_NoMemory();
		
	((PyDMIBlock *)p)->next = block_list;
	block_list = (PyDMIBlock *)p;
	p = &((PyDMIBlock *)p)->objects[0];
	q = p + N_INTOBJECTS;
	while (--q > p)
		q->ob_type = (struct _typeobject *)(q-1);
	q->ob_type = NULL;
	return p + N_INTOBJECTS - 1;
}

static PyDMI *
newPyDMI(PyObject *arg)
{
	register PyDMI *v;
	if (free_list == NULL) {
		if ((free_list = fill_free_list()) == NULL)
			return NULL;
	}
	/* PyObject_New is inlined */
	v = free_list;
	free_list = (PyDMI *)v->ob_type;

	PyObject_INIT(v, &PyDMI_Type);

	v->next=NULL;
	v->another=NULL;
	
	v->value=v->new_value=v->init_value=0.0;

	return (PyDMI *) v;
}


/* PyDMI methods */

static void
PyDMI_dealloc(PyDMI *v)
{
	Py_XDECREF(v->next);
	Py_XDECREF(v->another);

	v->ob_type = (struct _typeobject *)free_list;
	free_list = v;
}

static PyObject *
 __model_steps(PyDMI * xp, double dt, long num)
{
    PyDMI * p=xp, *d;
    long i=num;
    
    // Initialize new_value
    p=xp;
    while (p) {
        p->new_value=0.0;
        p = p->next;
    };
    
    while (i--) {
	p = xp;
	while (p) {
	    double arcs = 0.0;
	    d = p->another;
	    while (d) {
		double arc = d->value;
		arcs += arc;
		if (d->another == NULL) {
		PyErr_SetString(PyExc_ValueError, "bad prepared model (an arc refer to nowhere)");
		return NULL;
		};
	    
		d->another->new_value += arc * p->value * dt;
	    
		d = d->next;
	    };
	    p->new_value -= arcs * p->value * dt;
	
	    p = p->next;
	};
    
	// add new_value to value and reinitialize new_value
	p = xp;
	while (p) {
	    p->value += p->new_value;
	    p->new_value = 0.0;
	    p = p->next;
	};
    }; // while
    
    Py_INCREF(Py_None);
    return Py_None;
};

static PyObject *
 __model_reset(PyDMI * xp)
{
    PyDMI * p=xp, *d;
    
    // Initialize new_value
    p=xp;
    while (p) {
        p->new_value=0.0;
	p->value=p->init_value;
    	d = p->another;
	while (d) {
	    p->new_value=0.0;
	    p->value=p->init_value;
	    d = d->next;
	};
        p = p->next;
    };
    
    
    Py_INCREF(Py_None);
    return Py_None;
};

static PyObject * 
PyDMI_step(PyDMI *xp, PyObject * args) {
    double dt;
    long times=1L;
    int rc;
    
    rc=PyArg_ParseTuple(args, "d|l:step", & dt, & times);
    if (!rc) {
        return NULL;
    };
    
        
    // printf("dt=%f, times=%il, %il", dt, times, rc);
    
    if (xp == NULL || !PyDMI_Check(xp)) {
	PyErr_SetString(PyExc_RuntimeError, "wrong receiver object");
	return NULL;
    };
    if (dt <= 0.0) {
	PyErr_SetString(PyExc_ValueError, "modelling step must be graeter than sero");
	return NULL;
    };
    
    return __model_steps(xp, dt, times);
};

static PyObject * 
PyDMI_reset(PyDMI *xp, PyObject * args) {
    int rc;
    
    rc=PyArg_ParseTuple(args, ":step");
    if (!rc) {
        return NULL;
    };
    
        
    // printf("dt=%f, times=%il, %il", dt, times, rc);
    
    if (xp == NULL || !PyDMI_Check(xp)) {
	PyErr_SetString(PyExc_RuntimeError, "wrong receiver object");
	return NULL;
    };
    
    return __model_reset(xp);
};

static PyMethodDef PyDMI_methods[] = {
    {"step",	(PyCFunction) PyDMI_step, METH_VARARGS},
    {"reset",	(PyCFunction) PyDMI_reset, METH_VARARGS},
    {NULL,	NULL}
};

static PyObject * 
__get_link(PyDMI * xp) {
    if (xp) {
	Py_XINCREF(xp);
	return (PyObject *) xp;
    };
    Py_INCREF(Py_None);
    return Py_None;
};

static PyObject *
PyDMI_getattr(PyDMI *xp, char *name)
{
	if (strcmp(name,"total") == 0) {
	    register PyDMI * p=xp;
	    register double sum=0.0;
	    
	    while (p) {
		sum += p->value;
		p = p->next;
	    }
	    return PyFloat_FromDouble(sum);
	};


	if (strcmp(name,"value") == 0) {
	    return PyFloat_FromDouble(xp->value);
	};
	if (strcmp(name,"initValue") == 0) {
	    return PyFloat_FromDouble(xp->init_value);
	};
	if (strcmp(name,"newValue") == 0) {
	    return PyFloat_FromDouble(xp->new_value);
	};
	if (strcmp(name,"next") == 0) {
	    return __get_link(xp->next);
	};
	if (strcmp(name,"another") == 0) {
	    return __get_link(xp->another);
	};

	return Py_FindMethod(PyDMI_methods, (PyObject *)xp, name);
}


static int
__set_link(PyDMI ** to, PyObject * link) {
    if (link==Py_None) {
	if (*to) {
	    Py_DECREF(*to);
	};
	*to=NULL;
	return 0;
    };
    if (PyDMI_Check(link)) {
	if (*to) {
	    Py_DECREF(*to);
	};
	Py_INCREF(link);
	*to=(PyDMI *) link;
	return 0;
    };
    PyErr_SetString(PyExc_ValueError, "DMItem or None expected");
    return -1;
};

static int 
__set_var(double * val, PyObject *v) {
	if (PyFloat_Check(v)) {
	    *val = PyFloat_AsDouble(v);	
	    return 0;
	};
	if (PyInt_Check(v)) {
	    *val = PyInt_AsLong(v);	
	    return 0;
	};
	PyErr_SetString(PyExc_ValueError, "float or integer expected");
	return -1;
}

#define __ROF() PyErr_SetString(PyExc_AttributeError, \
		     "this is a read-only field"); \
	        return -1;


static int
PyDMI_setattr(PyDMI *xp, char *name, PyObject *v)
{
/*	if (xp->x_attr == NULL) {
		xp->x_attr = PyDict_New();
		if (xp->x_attr == NULL)
			return -1;
	}
	if (v == NULL) {
		int rv = PyDict_DelItemString(xp->x_attr, name);
		if (rv < 0)
			PyErr_SetString(PyExc_AttributeError,
                                        "delete non-existing xx attribute");
		return rv;
	}
	else
		return PyDict_SetItemString(xp->x_attr, name, v);
	*/
	
	if (strcmp(name,"value") == 0) {
	    return __set_var(& xp->value, v);
	};
	if (strcmp(name,"initValue") == 0) {
	    return __set_var(& xp->init_value, v);
	};
	if (strcmp(name,"next") == 0) {
	    return __set_link(& xp->next, v);
	};
	if (strcmp(name,"another") == 0) {
	    return __set_link(& xp->another, v);
	};
	
	if (strcmp(name,"newValue") == 0) {
	    __ROF()
	};
	if (strcmp(name,"agregated") == 0) {
	    __ROF()
	};
	
	PyErr_SetString(PyExc_AttributeError, "unknown field name");
	return -1;
}

static PyTypeObject PyDMI_Type = {
	PyObject_HEAD_INIT(0)
	0,			/*ob_size*/
	"DMItem",		/*tp_name*/
	sizeof(PyDMI),		/*tp_basicsize*/
	0,			/*tp_itemsize*/
	/* methods */
	(destructor)PyDMI_dealloc, /*tp_dealloc*/
	0,			/*tp_print*/
	(getattrfunc)PyDMI_getattr, /*tp_getattr*/
	(setattrfunc)PyDMI_setattr, /*tp_setattr*/
	0,			/*tp_compare*/
	0,			/*tp_repr*/
	0,			/*tp_as_number*/
	0,			/*tp_as_sequence*/
	0,			/*tp_as_mapping*/
	0,			/*tp_hash*/
};


/* --------------------------------------------------------------------- */

/* Function of no arguments returning new Xxo object */

static PyObject *
PyDMI_new(PyObject *self, PyObject *args)
{
	PyDMI *rv;
	
	if (!PyArg_ParseTuple(args, ":NewItem"))
		return NULL;
	rv = newPyDMI(args);
	if ( rv == NULL )
	    return NULL;
	return (PyObject *)rv;
};

/*
static PyObject *
PyDMI_destroy(PyDMI * self, PyObject * args) {
	PyDMI * p=self, * d, * n;	
    
	if (!PyArg_ParseTuple(args, ":Destroy")) {
	    return NULL;
	};
	
	while (p) {
	    Py_XDECREF(same);
	    ......
	    n = p -> next;
	    Py_XDECREF(p->other);
	    Py_XDECREF(p->next);
	    p = n;
	};
};
*/
static PyObject *
PyDMI_Fini(PyObject * self, PyObject * args)
{
	PyDMI *p;
	PyDMIBlock *list, *next;
	int i;
	int bc, bf;	/* block count, number of freed blocks */
	int irem, isum;	/* remaining unfreed ints per block, total */
	int verbose=0;
	
	if (!PyArg_ParseTuple(args, "|i:Finalize", &verbose)) {
	    return NULL;
	};
	
	bc = 0;
	bf = 0;
	isum = 0;
	list = block_list;
	block_list = NULL;
	free_list = NULL;
	
	while (list != NULL) {
		bc++;
		irem = 0;
		for (i = 0, p = &list->objects[0];
		     i < N_INTOBJECTS;
		     i++, p++) {
			if (PyDMI_Check(p) && p->ob_refcnt != 0) {
				irem++;
			}
		}
		next = list->next;
		if (irem) {
			list->next = block_list;
			block_list = list;
			for (i = 0, p = &list->objects[0];
			     i < N_INTOBJECTS;
			     i++, p++) {
				if (!PyDMI_Check(p) || p->ob_refcnt == 0) {
					p->ob_type = (struct _typeobject *)
						free_list;
					free_list = p;
				}
			}
		}
		else {
			PyMem_FREE(list); /* XXX PyObject_FREE ??? */
			bf++;
		}
		isum += irem;
		list = next;
	}
	if (!verbose){
		Py_INCREF(Py_None);
		return Py_None;
	};
	fprintf(stderr, "# cleanup DMIs");
	if (!isum) {
		fprintf(stderr, "\n");
	}
	else {
		fprintf(stderr,
			": %d unfreed DMI%s in %d out of %d block%s\n",
			isum, isum == 1 ? "" : "s",
			bc - bf, bc, bc == 1 ? "" : "s");
	}
	if (verbose > 1) {
		list = block_list;
		while (list != NULL) {
			for (i = 0, p = &list->objects[0];
			     i < N_INTOBJECTS;
			     i++, p++) {
				if (PyDMI_Check(p) && p->ob_refcnt != 0)
					fprintf(stderr,
				"#   <int at %p, refcnt=%d>\n",
						p, p->ob_refcnt);
			}
			list = list->next;
		}
	}
	Py_INCREF(Py_None);
	return Py_None;
}

// some functions

int calc_total(PyListObject * list, double * sum) 
{
	PyObject * x;
	int i, rc;
	
	for (i = list->ob_size; --i >= 0; ) {
		x = list->ob_item[i];
		if (x != NULL) {
			if (PyDMI_Check(x)) {
				* sum += ((PyDMI *) x) -> value;
			} else if (PyList_Check(x)){
				rc=calc_total((PyListObject *) x, sum);
				if (rc==0) 
					return 0;
			} else {
				PyErr_SetString(PyExc_ValueError,"not all sequence items are DMIs or lists");
				return 0;
			};
		}
	}
	return 1;
};

static PyObject *
PyList_Total(PyObject * self, PyObject * args)
{
	double initValue=0.0;
	PyListObject * list;
	
	if (args != NULL) {
		if (!PyArg_ParseTuple(args, "O|f:total", &list, &initValue))
			return NULL;
	}
	
	if (!PyList_Check(list)) {
		PyErr_SetString(PyExc_TypeError,"the first argument must be a list");
		return NULL;
	};
	
	if (calc_total(list, &initValue)==0) {
		return NULL;
	};

	return PyFloat_FromDouble(initValue);
};





/* List of functions defined in the module */

static PyMethodDef PyDMI_module_methods[] = {
	{"NewItem",	(PyCFunction) PyDMI_new,		METH_VARARGS},
	{"Finalize",	(PyCFunction) PyDMI_Fini,		METH_VARARGS},
	{"total",		(PyCFunction) PyList_Total,		METH_VARARGS},
	{NULL,		NULL}		/* sentinel */
};


/* Initialization function for the module (*must* be called initxx) */

DL_EXPORT(void)
initDModel(void)
{
	PyObject *m, *d;

	/* Initialize the type of the new type object here; doing it here
	 * is required for portability to Windows without requiring C++. */
	PyDMI_Type.ob_type = &PyType_Type;

	/* Create the module and add the functions */
	m = Py_InitModule("DModel", PyDMI_module_methods);

	/* Add some symbolic constants to the module */
	d = PyModule_GetDict(m);
	ErrorObject = PyErr_NewException("DModel.error", NULL, NULL);
	PyDict_SetItemString(d, "error", ErrorObject);
}


