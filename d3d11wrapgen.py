def Ind(N):
	return " " * N
def countPtrs(txt):
	result = 0
	for char in txt:
		if char == "*":
			result += 1
	return result
def dumpMethod(ctx, obj, Meth, declOnly):
	PN = len(Meth.params)
	if PN == 0:
		if declOnly:
			print(Ind(2) + Meth.retTy + " __stdcall " + Meth.name + "() override;")
		else:
			print(Ind(0) + Meth.retTy + " __stdcall Wrapped" + obj + "::" + Meth.name + "() {")
			print(Ind(2) + "out() << \"" + obj + "(\" << m_pWrapped << \")::" + Meth.name + "\\n\";")
			print(Ind(2) + "return m_pWrapped->" + Meth.name + "();")
			print(Ind(0) + "}")
	else:
		if declOnly:
			print(Ind(2) + Meth.retTy + " __stdcall " + Meth.name + "(")
			for Pi in range(0, PN):
				com = ", "
				if Pi == PN - 1:
					com = ""
				print(Ind(4) + Meth.params[Pi].type + " " + Meth.params[Pi].name + com)
			print(Ind(2) + ") override;")
		else:
			print(Ind(0) + Meth.retTy + " __stdcall Wrapped" + obj + "::" + Meth.name + "(")
			for Pi in range(0, PN):
				com = ", "
				if Pi == PN - 1:
					com = ""
				print(Ind(2) + Meth.params[Pi].type + " " + Meth.params[Pi].name + com)
			print(Ind(0) + ") {")
			
			print(Ind(2) + "out() << \"" + obj + "(\" << m_pWrapped << \")::" + Meth.name + "\\n\";")
			####### PRE-PROCESS
			NumWrapped = ""
			#if Meth.name in ["QueryInterface"]:
				#NumWrapped = 
			# for scalar, ptr and array types there is different unwrap code
			UnwrapTable = {}
			for param in Meth.params:
				if countPtrs(param.type) == 2 and param.annot in ["IN_ARRAY", "INOUT_ARRAY"]:
					print(Ind(2) + param.type.split("*")[0].replace("const", "") + " *tmp_" + param.name + "[32];")
					print(Ind(2) + "for (int i = 0; i < " + param.number + "; i++) tmp_" + param.name + "[i] = unwrap(" + param.name + "[i]);")
					UnwrapTable[param.name] = "tmp_" + param.name + ""
				elif countPtrs(param.type) == 1 and param.annot in ["IN", "INOUT"]:
					UnwrapTable[param.name] = "unwrap(" + param.name + ")"
				else:
					UnwrapTable[param.name] = param.name

			####### CALL
			if Meth.retTy == "void":
				print(Ind(2) + "m_pWrapped->" + Meth.name + "(")
			else:
				print(Ind(2) + "auto ret = m_pWrapped->" + Meth.name + "(")
			for Pi in range(0, PN):
				com = ", "
				if Pi == PN - 1:
					com = ""
				print(Ind(4) + UnwrapTable[Meth.params[Pi].name] + com)
			print(Ind(2) + ");")
			####### POST-PROCESS
			if Meth.name in ["GetDevice"]:
				print(Ind(2) + "if(*" + Meth.params[-1].name + ")")
				print(Ind(4) + "HandleWrap(__uuidof(ID3D11Device), (void**)" + Meth.params[-1].name + ");")
			elif Meth.name in ["GetResource"]:
				print(Ind(2) + "if(*" + Meth.params[-1].name + ")")
				print(Ind(4) + "HandleWrap(__uuidof(ID3D11Resource), (void**)" + Meth.params[-1].name + ");")
			elif Meth.name in ["OpenSharedResource", "OpenSharedFence", "CreateFence"]:
				print(Ind(2) + "if(*" + Meth.params[-1].name + ")")
				print(Ind(4) + "HandleWrap(ReturnedInterface, (void**)" + Meth.params[-1].name + ");")
			elif Meth.name in ["GetCoreWindow"]:
				print(Ind(2) + "if(*" + Meth.params[-1].name + ")")
				print(Ind(4) + "HandleWrap(refiid, (void**)" + Meth.params[-1].name + ");")
			elif Meth.name in ["OpenSharedResourceByName", "OpenSharedResource1"]:
				print(Ind(2) + "if(*" + Meth.params[-1].name + ")")
				print(Ind(4) + "HandleWrap(returnedInterface, (void**)" + Meth.params[-1].name + ");")
			elif Meth.name in ["QueryInterface", "GetParent",
			"GetBuffer",
			"EnumAdapterByLuid", "EnumWarpAdapter"]:
				print(Ind(2) + "{")
				print(Ind(4) + "if(!ret) {")
				print(Ind(6) + "HandleWrap(riid, " + Meth.params[-1].name + ");")
				print(Ind(4) + "}")
				print(Ind(2) + "}")
			elif Meth.name in ["GetDecoderBuffer"]:
				print(Ind(2) + "assert(false && \"Wrap not implemented; Emit Seg Fault\");")
			else:
				for param in Meth.params:
					if countPtrs(param.type) == 2 and param.annot in ["INOUT_ARRAY"]:
						RawType = param.type.split(" ")[0]
						if RawType == "struct":
							RawType = param.type.split(" ")[1]
						if RawType in ctx.apiTypes.keys():
							print(Ind(2) + "for (int i = 0; i < " + param.number + "; i++) if (tmp_" + param.name + "[i]) " + param.name + "[i] = getWrapper<" + RawType +
							", Wrapped" + RawType + ">(tmp_" + param.name + "[i]);")
					if countPtrs(param.type) == 2 and param.annot in ["OUT_ARRAY"]:
						RawType = param.type.split(" ")[0]
						if RawType == "struct":
							RawType = param.type.split(" ")[1]
						if RawType in ctx.apiTypes.keys():
							print(Ind(2) + "for (int i = 0; i < " + param.number + "; i++) if (" + param.name + " && " + param.name + "[i]) " + param.name + "[i] = getWrapper<" + RawType +
							", Wrapped" + RawType + ">(" + param.name + "[i]);")
					elif countPtrs(param.type) == 1 and param.annot in ["OUT", "INOUT"]:
						RawType = param.type.split(" ")[0]
						if RawType == "struct":
							RawType = param.type.split(" ")[1]
						if RawType in ctx.apiTypes.keys():
							print(Ind(4) + "if (" + param.name + " && *" + param.name  + " ) *" + param.name + " = getWrapper<" + RawType + ", Wrapped" + RawType + ">(*" + param.name + ");")
					else:
						pass
			""""
				for Pi in range(0, PN):
					if "**" in Meth.params[Pi].type:
						RawType = Meth.params[Pi].type.split(" ")[0]
						if RawType == "struct":
							RawType = Meth.params[Pi].type.split(" ")[1]
						print(Ind(2) + "if (*" + Meth.params[Pi].name + ")")
						#print(Ind(4) + "*" + Meth.params[Pi].name + " = new Wrapped" + RawType + "(*" + Meth.params[Pi].name + ");")
						print(Ind(4) + "*" + Meth.params[Pi].name + " = getWrapper<" + RawType +
						", Wrapped" + RawType + ">(*" + Meth.params[Pi].name + ");")
						"""
			if Meth.retTy != "void":
				print(Ind(2) + "return ret;")
			print(Ind(0) + "}")
	
def genQueryImpl(ctx):
	print("""template<typename T> void HandleWrap(
  const IID & riid, 
  T ** ppvObject) {""")
	#print(Ind(2) + "HRESULT hr = S_OK;")
	for TyName, Ty in ctx.apiTypes.items():
		if TyName == "ID3DInclude":
			continue
		print(Ind(2) + "if(riid == __uuidof(" + Ty.name + ")) {")
		print(Ind(4) + "*ppvObject = (T*)getWrapper<" + Ty.name +
						", Wrapped" + Ty.name + ">((" + Ty.name + "*)*ppvObject);")
		print(Ind(4) + "return;")
		print(Ind(2) + "}")
	print(Ind(2) + "{")
	print(Ind(4) + "out() << \"[WARNING] Unknown(\" << *ppvObject << \") riid:\" << riid << \"\\n\";")
	#print(Ind(4) + "return pObj->" + name + "(riid, ppvObject);")
	#print(Ind(4) + "assert(false && \"Wrap not implemented; Emit Seg Fault\");")
	print(Ind(2) + "}")
	#print(Ind(2) + "return S_OK;")
	print(Ind(0) + "}")

def genWrappers(ctx):
	print("""#include <d3d11.h>
#include <d3d11_1.h>
#include <d3d11_2.h>
#include <d3d11_3.h>
#include <d3d11_4.h>
#include <d3dcompiler.h>
#include <dxgi.h>
#include <dxgi1_2.h>
#include <dxgi1_3.h>
#include <dxgidebug.h>
#include <unordered_map>
#include <fstream>
#include <assert.h>
static std::ofstream &out()
{
  static std::ofstream file("log");
  file.setf(std::ios::unitbuf);
  return file;
}
static std::unordered_map<size_t, size_t> &getWrapTable()
{
  static std::unordered_map<size_t, size_t> table;
  return table;
}
static std::unordered_map<size_t, size_t> &getUnwrapTable()
{
  static std::unordered_map<size_t, size_t> table;
  return table;
}
template<typename T, typename WT>
T *getWrapper(T *t)
{
  auto &wt = getWrapTable();
  auto fd = wt.find(reinterpret_cast<size_t>((void*)t));
  if (fd == wt.end()) {
    auto *wrap = new WT(t);
    auto &uwt = getUnwrapTable();
    uwt.emplace(reinterpret_cast<size_t>((void*)wrap), reinterpret_cast<size_t>((void*)t));
    wt.emplace(reinterpret_cast<size_t>((void*)t), reinterpret_cast<size_t>((void*)wrap));
    return reinterpret_cast<T*>(wrap);
  }
  else
  {
    return reinterpret_cast<T*>((*fd).second);
  }
}
template<typename T>
T *unwrap(T *t)
{
  auto &uwt = getUnwrapTable();
  auto fd = uwt.find(reinterpret_cast<size_t>((void*)t));
  if (fd == uwt.end()) {
    return t;
  }
  else
  {
    return reinterpret_cast<T*>((*fd).second);
  }
}
std::ostream& operator<<(std::ostream& os, REFGUID guid) {

  os << std::uppercase;
  os.width(8);
  os << std::hex << guid.Data1 << '-';

  os.width(4);
  os << std::hex << guid.Data2 << '-';

  os.width(4);
  os << std::hex << guid.Data3 << '-';

  os.width(2);
  os << std::hex
    << static_cast<short>(guid.Data4[0])
    << static_cast<short>(guid.Data4[1])
    << '-'
    << static_cast<short>(guid.Data4[2])
    << static_cast<short>(guid.Data4[3])
    << static_cast<short>(guid.Data4[4])
    << static_cast<short>(guid.Data4[5])
    << static_cast<short>(guid.Data4[6])
    << static_cast<short>(guid.Data4[7]);
  os << std::nouppercase;
  return os;
}
""")
	genQueryImpl(ctx)

	for TyName, Ty in ctx.apiTypes.items():
		print("#if 0")
		Ty.dump(ctx)
		print("#endif")
		print("class Wrapped" + TyName + " : public " + TyName + " {")
		print("private:")
		print(Ind(2) + TyName + " *m_pWrapped;")
		print("public:")
		print(Ind(2) + "Wrapped" + TyName + "(" + TyName + " *pWrapped) : m_pWrapped(pWrapped) {")
		print(Ind(4) + "out() << \"[CREATE] " + TyName + "(\" << m_pWrapped << \")\\n\";")
		if Ty.hasBase(ctx, "IUnknown"):
			print(Ind(4) + "for (int i = 0; i < 10; i++) m_pWrapped->AddRef();")
		print(Ind(2) + "}")

		MethSet = {}
		for Meth in Ty.methods:
			MethSet[Meth.name] = Meth
			#dumpMethod(TyName, Meth, True)
		for Base in Ty.getBases(ctx, []):
			for Meth in Base.methods:
				MethSet[Meth.name] = Meth
				#print("//inherited from " + Base.name)
				#dumpMethod(TyName, Meth, True)
		for Name, Meth in MethSet.items():
			dumpMethod(ctx, TyName, Meth, True)
		print("};")
	print("typedef WrappedID3D10Blob WrappedID3DBlob;")
	for TyName, Ty in ctx.apiTypes.items():

		MethSet = {}
		for Meth in Ty.methods:
			MethSet[Meth.name] = Meth
		for Base in Ty.getBases(ctx, []):
			for Meth in Base.methods:
				MethSet[Meth.name] = Meth
		for Name, Meth in MethSet.items():
			dumpMethod(ctx, TyName, Meth, False)	
		
		
	for FName, FTy in ctx.apiFuncs.items():
		PN = len(FTy.params)
		if PN == 0:
			print(Ind(0) + FTy.retTy + " Wrapped" + FTy.name + "() {")
			print(Ind(2) + "out() << \"" + FTy.name + "\\n\";")
			print(Ind(2) + "return " + FTy.name + "();")
			print(Ind(0) + "}")
		else:
			print(Ind(0) + FTy.retTy + " Wrapped" + FTy.name + "(")
			for Pi in range(0, PN):
				com = ", "
				if Pi == PN - 1:
					com = ""
				print(Ind(2) + FTy.params[Pi].type + " " + FTy.params[Pi].name + com)
			print(Ind(0) + ") {")
			print(Ind(2) + "out() << \"" + FTy.name + "\\n\";")
			if FTy.retTy == "void":
				print(Ind(2) + "" + FTy.name + "(")
			else:
				print(Ind(2) + "auto ret = " + FTy.name + "(")
			for Pi in range(0, PN):
				com = ", "
				if Pi == PN - 1:
					com = ""
				print(Ind(4) + FTy.params[Pi].name + com)
			print(Ind(2) + ");")
			if FTy.name in ["D3DReflect"]:
				print(Ind(2) + "assert(false && \"Wrap not implemented; Emit Seg Fault\");")
			elif FTy.name in ["DXGIGetDebugInterface", "DXGIGetDebugInterface1",
			"CreateDXGIFactory2", "CreateDXGIFactory", "CreateDXGIFactory1"]:
				print(Ind(2) + "if(ret)")
				print(Ind(4) + "HandleWrap(riid, (void**)" + FTy.params[-1].name + ");")
			else:
				for Pi in range(0, PN):
					if "**" in FTy.params[Pi].type:
						RawType = FTy.params[Pi].type.split(" ")[0]
						if RawType == "struct":
							RawType = FTy.params[Pi].type.split(" ")[1]
						print(Ind(2) + "if (*" + FTy.params[Pi].name + ")")
						print(Ind(4) + "*" + FTy.params[Pi].name + " = getWrapper<" + RawType +
						", Wrapped" + RawType + ">(*" + FTy.params[Pi].name + ");")
			
			if FTy.retTy != "void":
				print(Ind(2) + "return ret;")
			print(Ind(0) + "}")
