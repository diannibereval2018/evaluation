def precision(tp,fp):
	return tp/float(tp+fp)

def recall(tp,fn):
	return tp/float(tp+fn)

def f1score(tp,fp,fn):
	return (2*tp)/float(2*tp+fp+fn)
