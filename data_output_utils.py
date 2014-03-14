import numpy as np
import scipy.io
import json
from dolfin_to_sparrays import expand_vp_dolfunc
import dolfin


def output_paraview(V=None, Q=None, fstring='nn',
                    invinds=None, diribcs=None,
                    vp=None, vc=None, pc=None,
                    t=None, writeoutput=True,
                    vfile=None, pfile=None):
    """write the paraview output for a solution vector vp

    """

    if not writeoutput:
        return

    v, p = expand_vp_dolfunc(V=V, Q=Q, vp=vp,
                             vc=vc, pc=pc,
                             invinds=invinds,
                             diribcs=diribcs)

    v.rename('v', 'velocity')
    if vfile is None:
        vfile = dolfin.File(fstring+'_vel.pvd')
    vfile << v, t
    if p is not None:
        p.rename('p', 'pressure')
        if pfile is None:
            pfile = dolfin.File(fstring+'_p.pvd')
        pfile << p, t


def save_npa(v, fstring='notspecified'):
    np.save(fstring, v)
    return


def load_npa(fstring):
    return np.load(fstring+'.npy')


def save_spa(sparray, fstring='notspecified'):
    scipy.io.mmwrite(fstring, sparray)


def load_spa(fstring):
    return scipy.io.mmread(fstring).tocsc()


def load_json_dicts(StrToJs):
    fjs = open(StrToJs)
    JsDict = json.load(fjs)
    return JsDict


def plot_outp_sig(str_to_json=None, tmeshkey='tmesh', sigkey='outsig',
                  outsig=None, tmesh=None, fignum=222, reference=None,
                  compress=5):
    import matplotlib.pyplot as plt
    from matplotlib2tikz import save as tikz_save

    if str_to_json is not None:
        jsdict = load_json_dicts(str_to_json)
        tmesh = jsdict[tmeshkey]
        outsig = jsdict[sigkey]
    else:
        str_to_json = 'notspecified'

    redinds = range(1, len(tmesh), compress)
    redina = np.array(redinds)

    NY = len(outsig[0])/2

    fig = plt.figure(fignum)
    ax1 = fig.add_subplot(111)
    ax1.plot(np.array(tmesh)[redina], np.array(outsig)[redina, :NY],
             color='b', linewidth=2.0)
    ax1.plot(np.array(tmesh)[redina], np.array(outsig)[redina, NY:],
             color='r', linewidth=2.0)

    tikz_save(str_to_json + '{0}'.format(fignum) + '.tikz',
              figureheight='\\figureheight',
              figurewidth='\\figurewidth'
              )
    print 'tikz saved to ' + str_to_json + '{0}'.format(fignum) + '.tikz'
    fig.show()

    if reference is not None:
        fig = plt.figure(fignum+1)
        ax1 = fig.add_subplot(111)
        ax1.plot(tmesh, np.array(outsig)-reference)

        tikz_save(str_to_json + '{0}'.format(fignum) + '_difftoref.tikz',
                  figureheight='\\figureheight',
                  figurewidth='\\figurewidth'
                  )
        fig.show()


def save_output_json(datadict=None,
                     fstring='unspecified_outputfile',
                     module='dolfin_navier_scipy.data_output_utils',
                     plotroutine='plot_outp_sig'):
    """save output to json for postprocessing

    """

    jsfile = open(fstring, mode='w')
    jsfile.write(json.dumps(datadict))

    print 'output saved to ' + fstring
    print '\n to plot run the commands \n'
    print 'from ' + module + ' import ' + plotroutine
    print plotroutine + '("' + fstring + '")'


def extract_output(dictofpaths=None, tmesh=None, c_mat=None, ystarvec=None):

    cur_v = load_npa(dictofpaths[tmesh[0]])
    yn = c_mat*cur_v
    yscomplist = [yn.flatten().tolist()]
    for t in tmesh[1:]:
        cur_v = load_npa(dictofpaths[tmesh[t]])
        yn = c_mat*cur_v
        yscomplist.append(yn.flatten().tolist())
    if ystarvec is not None:
        ystarlist = [ystarvec(0).flatten().tolist()]
        for t in tmesh[1:]:
            ystarlist.append(ystarvec(0).flatten().tolist())

        return yscomplist, ystarlist

    else:
        return yscomplist
