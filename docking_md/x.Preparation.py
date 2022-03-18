import os,subprocess,wget,shutil,gzip
from pybel import *
class Protein_prep:
    def __init__(self,RosettaPath):
        self.RPath = RosettaPath
    def clean_by_rosetta(self,pid,cid):
        scripts_path = os.path.join(self.RPath,"tools/protein_tools/scripts/")

        url = 'http://www.rcsb.org/pdb/files/%s.pdb.gz'%pid
        wget.download(url)
        with gzip.open("%s.pdb.gz"%pid.lower(),"rb") as F:
            with open("%s.pdb"%pid,"wb") as W:
                shutil.copyfileobj(F,W)

        subprocess.call("%s/clean_pdb.py %s %s"%(scripts_path,pid,cid),shell=True)

    def extract_origin_ligand(self,pid):
        tline = []
        with open("%s.pdb"%pid,"r") as F:
            for line in F.readlines():
                if line.startswith("HETATM"):
                    tline.append(line.strip())
                else:
                    pass
        with open("%s_lig.pdb"%pid,"w") as W:
            for line in tline:
                W.write(line + "\n")
        subprocess.call("obabel %s_lig.pdb -O %s_lig.mol2"%(pid,pid),shell=True)

class Ligand_prep:
    def __init__(self,RosettaPath):
        self.RPath = RosettaPath
    def Make_3D_by_pybel(self,ismi,iname):
        pmol = readstring("smi",ismi)
        pmol.make3D()
        pmol.removeh()
        output = Outputfile("mol2",iname+".mol2")
        output.write(pmol)
        output.close()

    def Move_ligand_to_origin(self,ls_path,iname,iiname):
        tline = []
        subprocess.call("%s/LSalign %s.mol2 ../%s_lig.mol2 -o temp.pdb"%(ls_path,iname,iiname),shell=True)
        with open('temp.pdb',"r") as F:
            for line in F.readlines():
                if line.startswith("TER"):
                    break
                else:
                    tline.append(line.strip())
        with open("%s_mv.pdb"%iname,"w") as W:
            for line in tline:
                W.write(line + "\n")
        pmol = next(readfile("pdb","%s_mv.pdb"%iname))
        pmol.removeh()
        output = Outputfile("sdf",iname+".sdf")
        output.write(pmol)
        output.close()

    def Make_Conformers(self,iname):
        subprocess.call("obabel %s.sdf -O conf1.sdf --conformer --nconf 500 --score rmsd --writeconformers"%(iname),shell=True)
        subprocess.call("obabel %s.sdf -O conf2.sdf --conformer --nconf 500 --score energy --writeconformers"%(iname),shell=True)
        os.system("cat conf1.sdf conf2.sdf > %s_conf.sdf"%(iname))

    def Make_Rosetta_Params(self,nn,pf,iname):
        scripts_path = os.path.join(self.RPath,"source/scripts/python/public")
        subprocess.call("python %s/molfile_to_params.py -n %s -p %s --conformers-in-one-file %s_conf.sdf"%(scripts_path,nn,pf,iname),shell=True)