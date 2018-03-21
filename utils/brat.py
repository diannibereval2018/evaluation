def generate_ann(anotated):
    pre_to_translate = {"dis":["Disability","T",(0,0)],"neg":["Neg","T",(0,0)],"scp":["Scope","T",(0,0)]}
    i,x,text = 1,0,""
    state = 0
    inclu = []
    chest = dict()
    anotated = anotated.strip()
    for charac in anotated:
        if state==0:
            if charac=="<" and len(anotated)>x+4 and anotated[x+1:x+4] in pre_to_translate:       
                if not anotated[x+1:x+4] in chest:
                    chest[anotated[x+1:x+4]] = list()
                chest[anotated[x+1:x+4]].append({"sent":"","beg":i,"end":-1})
                state = 4
                inclu.append(True)
            elif len(anotated)>x+5 and anotated[x:x+2]=="</" and anotated[x+2:x+5] in pre_to_translate:              
                for d in chest[anotated[x+2:x+5]]:
                    if d["end"]<0:
                        d["end"]=i
                state = 5
                inclu.remove(True)
            elif any(inclu):
                for c in chest: 
                    for d in chest[c]:
                        if d["end"]<0:
                            d["sent"] += charac
                i+=1
        else:
            state-=1
        x+=1
    aux = list()
    for clases in chest:
        for terms in chest[clases]:
            aux.append("T"+str(len(aux)+1)+"\t"+pre_to_translate[clases][0]+" "+str(terms["beg"])+" "+str(terms["end"])+"\t"+terms["sent"])
    return "\n".join(aux)
