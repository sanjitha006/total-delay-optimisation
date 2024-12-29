import time 
import sys
startime=time.time()
input_file=open("input.txt","r")
output_file=open("output.txt","w")


gwh=[]
pin_coord=[]
wire_con=[]
totalarea=0
totalh=0
totalw=0
maxh=0
g_delay=[]
output_pins=[]
gwh_groups=[]
gates={}

while(True):
    y=input_file.readline().split()

    if len(y)==0:
        break
    if(y[0]=="wire_delay"):
       w_delay=int(y[1])   
    elif(y[0][0]=="g"):
        x=[y[0],int(y[1]),int(y[2])]
        gwh.append(x)
        g_delay.append(y[3])
        
        maxh=max(maxh,int(y[2]))
        totalh+=int(y[2])
        totalw+=int(y[1])
        totalarea+=(int(y[1])*int(y[2]))
    elif(y[0][0]=="p"):
        x=[]
        no_pins=0
        for j in range(2,len(y)-1,2):
            x.append((int(y[j]),int(y[j+1])))
            no_pins+=1    
        output_pins.append([[] for i in range(no_pins)])
        pin_coord.append(x)
    elif(y[0][0]=="w"):        
        gate_name=y[1].split(".")
        gate_name_2=y[2].split(".")
        h=[gate_name[0],gate_name_2[0]]       
        x=[y[1],y[2]]
        wire_con.append(x)


for i in wire_con:
    x=i[0].split(".")
    gate_index_1=int(x[0][1::])-1
    pin_index_1=int(x[1][1::])-1
    y=i[1].split(".")
    gate_index_2=int(y[0][1::])-1
    pin_index_2=int(y[1][1::])-1

    if(pin_coord[gate_index_1][pin_index_1][0]==0):#input pin check        
        output_pins[gate_index_2][pin_index_2].append(i[0])
        if(output_pins[gate_index_1][pin_index_1]!=[]):
            print("error, same pin as input and output")
        output_pins[gate_index_1][pin_index_1]="i"
        
    elif(pin_coord[gate_index_1][pin_index_1][0]!=0):#output pin check
        output_pins[gate_index_1][pin_index_1].append(i[1])
        if(output_pins[gate_index_2][pin_index_2]!=[]):
            print("error, same pin as input and output")
        output_pins[gate_index_2][pin_index_2]="i"

for i in range(len(output_pins)):
    for j in range(len(output_pins[i])):
        if(output_pins[i][j]==[]):
            if(pin_coord[i][j][0]==0):
                output_pins[i][j]="pi"
            else:
                output_pins[i][j]="po"
        elif(output_pins[i][j]!="i"):
            output_pins[i][j]=[0,output_pins[i][j]]
            


def wire_len_calc(l):
    ans=0
    
    minx=sys.maxsize
    maxx=-1
    miny=sys.maxsize
    maxy=-1
    for j in l:
        if(j[0]<minx):
            minx=j[0]
        if(j[0]>maxx):
            maxx=j[0]
        if(j[1]<miny):
            miny=j[1]
        if(j[1]>maxy):
            maxy=j[1]
    ans+=((maxx-minx)+(maxy-miny))
    return(ans)

def allot_wire_delays(w_delay,final_pin_coord):
    for j in range(len(output_pins)):
        for i in range(len(output_pins[j])):
            pin=output_pins[j][i]
            if(pin!="i" and pin!="pi" and pin!="po"):
                l=[]
                l.append(final_pin_coord[j][i])
                for h in pin[1]:
                 
                    y=h.split(".")
                    gate_ind=int(y[0][1::])-1
                    pin_ind=int(y[1][1::])-1
                    l.append(final_pin_coord[gate_ind][pin_ind])

                delay=wire_len_calc(l)*w_delay
                output_pins[j][i][0]=delay

def critical_path(final_pin_coord, output_pins, g_delay):
 
    dp = {}

    def dfs(gate_idx, pin_idx):
      
        if (gate_idx, pin_idx) in dp:
            return dp[(gate_idx, pin_idx)]

        max_delay = 0
        max_path = []

        pin = output_pins[gate_idx][pin_idx]

        
        if pin == "po":
            return 0, [f"g{gate_idx+1}.p{pin_idx+1}"]

        
        if isinstance(pin, list) and pin != "pi" and pin != "i":
            wire_delay = pin[0]  
            connections = pin[1] 

            for connection in connections:
                next_gate, next_pin = connection.split(".")
                next_gate_idx = int(next_gate[1:]) - 1  
                next_pin_idx = int(next_pin[1:]) - 1

                for next_out_pin_idx, next_out_pin in enumerate(output_pins[next_gate_idx]):
                    if next_out_pin != "pi" and next_out_pin != "i":
                       
                        new_delay, returned_path = dfs(
                            next_gate_idx, next_out_pin_idx
                        )

                        total_delay = new_delay + wire_delay + int(g_delay[next_gate_idx])
                        returned_path=[f"g{gate_idx+1}.p{pin_idx+1}",f"g{next_gate_idx+1}.p{next_pin_idx+1}"]+returned_path
                       
                        if total_delay > max_delay:
                            max_delay = total_delay
                            max_path = returned_path

        
        dp[(gate_idx, pin_idx)] = (max_delay, max_path)
        return max_delay, max_path

    max_total_delay = 0
    max_total_path = []

 
    for gate_idx, pins in enumerate(output_pins):
        for pin_idx, pin in enumerate(pins):
            if pin == "pi": 
                initial_gate_delay = int(g_delay[gate_idx])
                path_so_far = [f"g{gate_idx+1}.p{pin_idx+1}"]
                
                for connection_idx, connected_pin in enumerate(pins):
                    if connected_pin != "i" and connected_pin != "pi" and connected_pin != "po":
                        delay, path = dfs(gate_idx, connection_idx)

                        total_delay = delay + initial_gate_delay
                        path=path_so_far+path
                        
                        if total_delay > max_total_delay:
                            max_total_delay = total_delay
                            max_total_path = path

   
    return max_total_delay, max_total_path

visited = [0] *( len(output_pins)+1)
gatename_groups=[]    
def append_new_group():
    new_grp=[]
    
    for i in gatename_groups[-1]:
        for j in (output_pins[i-1]):
            if(j!="pi" and j!="po" and j!="i"):
               for h in j[1]:
                   g=h.split(".")
                   g_num=int(g[0][1::])
                   if(visited[g_num]==0):
                      new_grp.append(g_num)
                      visited[g_num]=1
    if(new_grp==[]):
        return 0
    gatename_groups.append(new_grp)
    return 1

first_new=[]
for gate_idx, pins in enumerate(output_pins):
    for pin_idx, pin in enumerate(pins):
        if (pin == "pi" and visited[gate_idx+1]==0):
            first_new.append(gate_idx+1)
            visited[gate_idx+1]=1
gatename_groups.append(first_new)
while(True):
    if(append_new_group()==0):
        break

        


for group in gatename_groups:
    group_gwh = []  

    for gate_num in group:
        for g in gwh:
            if g[0] == f"g{gate_num}":  
                group_gwh.append(g) 

    gwh_groups.append(group_gwh)

for i in range(len(gwh_groups)):
    gwh_groups[i] = sorted(gwh_groups[i], key=lambda x: x[1], reverse=True)





def compute(avght,gwh_groups):
    def compute_cluster(avght,gwh_part,start_x):
        gates_temp={}
        fg=[]
        visited=[0]*(len(gwh_part))
        i=0
        bbheight2=avght
        
        while(i<len(gwh_part)):
            if (visited[i]==1):
                i+=1
                continue

            x=list([gwh_part[i]])
       
            visited[i]=1
          
            for j in range(i+1,len(gwh_part)):
              
                if((gwh_part[j][2]+gwh_part[i][2])<=avght and visited[j]!=1):
        
                    x=list([gwh_part[j]+["t"]])+x
                
                    visited[j]=1
                 
                    present_th=x[1][2]+x[0][2]
                    present_rh=x[1][2]
                    l=1
                    lb=0
                    p=1
                    for h in range(j+1,len(gwh_part)):
                        if(lb>=0 and ((x[l][1]-x[lb][1])>=gwh_part[h][1]) and ((gwh_part[h][2]+present_rh)<=avght) and p!=0 and visited[h]!=1):
                            present_rh+=x[l][2]
                            x.append(gwh_part[h]+["r"])
                    
                            l-=1
                            lb-=1
                            visited[h]=1
                            p-=1
                        elif((gwh_part[h][2]+present_th)<=avght and visited[h]==0 ):
                            x=list([gwh_part[h]+["t"]])+x
                          
                            p+=1
                            l+=1
                            lb+=1
                            present_th+=gwh_part[h][2]
                            visited[h]=1
                    break
                
            fg.append(x)

        k=start_x 
        
        for i in fg:
            if(len(i)>=2):
                for d in range(len(i)):
                    if(len(i[d])==3):
                        break
                gates_temp[i[d][0]]=(k,0)
                p=1
         
                while((d-p)>=0 or (d+p)<len(i) ):
                    if  (d-p)>=0:
                        gates_temp[i[d-p][0]]=(k,gates_temp[i[d-p+1][0]][1]+i[d-p+1][2])
                    if((d+p)<len(i)):
                        gates_temp[i[d+p][0]]=(gates_temp[i[d-p][0]][0]+i[d-p][1],gates_temp[i[d-p][0]][1])
                    p+=1
                k+=i[d][1]
                
            elif(len(i)==2):
                gates_temp[i[1][0]]=(k,0)
                gates_temp[i[0][0]]=(k,i[1][2])
                k+=i[1][1]
            else:
                gates_temp[i[0][0]]=(k,0)
                k+=i[0][1]

        return ([k,gates_temp])

    gates2={}
    start_x=0
    for c in gwh_groups:
        r=(compute_cluster(avght,c,start_x))
        start_x=r[0]
        
        gates2.update(r[1])
    
    bbwidth2=start_x
    final_pin_coord=[]
    for i in range(len(pin_coord)):
        k=[]
        for j in (pin_coord[i]):
            t=[]
            t.append(j[0]+gates2["g"+str(i+1)][0])
            t.append(j[1]+gates2['g'+str(i+1)][1])
            k.append(t)
        
        final_pin_coord.append(k)

    res=[final_pin_coord,bbwidth2,avght,gates2]

    return(res)
    
def compute(avght,gwh_clusters):
    def compute_cluster(avght,gwh_part,start_x):
        gates_temp={}
        fg=[]

        visited=[0]*(len(gwh_part))
        i=0
        bbheight2=avght
        
        while(i<len(gwh_part)):
            if (visited[i]==1):
                i+=1
                continue

            x=list([gwh_part[i]])
       
            visited[i]=1
          
            for j in range(i+1,len(gwh_part)):
                if((gwh_part[j][2]+gwh_part[i][2])<=avght and visited[j]!=1):
        
                    x=list([gwh_part[j]+["t"]])+x
                
                    visited[j]=1
                 
                    present_th=x[1][2]+x[0][2]
                    present_rh=x[1][2]
                    l=1
                    lb=0
                    p=1
                    for h in range(j+1,len(gwh_part)):
                        if(lb>=0 and ((x[l][1]-x[lb][1])>=gwh_part[h][1]) and ((gwh_part[h][2]+present_rh)<=avght) and p!=0 and visited[h]!=1):
                            present_rh+=x[l][2]
                            x.append(gwh_part[h]+["r"])
                    
                            l-=1
                            lb-=1
                            visited[h]=1
                            p-=1
                        elif((gwh_part[h][2]+present_th)<=avght and visited[h]==0 ):
                            x=list([gwh_part[h]+["t"]])+x
                          
                            p+=1
                            l+=1
                            lb+=1
                            present_th+=gwh_part[h][2]
                            visited[h]=1
                    break
                
            fg.append(x)

        k=start_x#chaneg this k to previous bound box ka x coordinate,,that is give this k as input to this function result has gates with correct coordinate finally merge all the gates or iterate through each and every gate and prnint in output file
        
        for i in fg:
            if(len(i)>=2):
                for d in range(len(i)):
                    if(len(i[d])==3):
                        break
                gates_temp[i[d][0]]=(k,0)
                p=1
         
                while((d-p)>=0 or (d+p)<len(i) ):
                    if  (d-p)>=0:
                        gates_temp[i[d-p][0]]=(k,gates_temp[i[d-p+1][0]][1]+i[d-p+1][2])
                    if((d+p)<len(i)):
                        gates_temp[i[d+p][0]]=(gates_temp[i[d-p][0]][0]+i[d-p][1],gates_temp[i[d-p][0]][1])
                    p+=1
                k+=i[d][1]
                
            elif(len(i)==2):
                gates_temp[i[1][0]]=(k,0)
                gates_temp[i[0][0]]=(k,i[1][2])
                k+=i[1][1]
            else:
                gates_temp[i[0][0]]=(k,0)
                k+=i[0][1]

        
        return ([k,gates_temp])

    gates_2=[]
    start_x=0
    for c in gwh_clusters:
       
        
        r=(compute_cluster(avght,c,start_x))
        start_x=r[0]
        gates_2.append(r[1])
        

    gates2 = {} 

    for d in gates_2:

        gates2.update(d)

    bbwidth2=start_x
    final_pin_coord=[]
    for i in range(len(pin_coord)):
        k=[]
        for j in (pin_coord[i]):
            t=[]
            t.append(j[0]+gates2["g"+str(i+1)][0])
            t.append(j[1]+gates2['g'+str(i+1)][1])
            k.append(t)
        
        final_pin_coord.append(k)


    res=[final_pin_coord,bbwidth2,avght,gates2]

    return(res)
    

def detect_cycles(output_pins):
    visited = [0] * len(output_pins)  

    def dfs(gate_index):
        if visited[gate_index] == 1:  
            return True
        if visited[gate_index] == 2: 
            return False

        visited[gate_index] = 1  
        for pin in output_pins[gate_index]:
            if pin != "pi" and pin != "po" and pin != "i":  
                connections = pin[1]  
                for connection in connections:
                    xx=connection.split(".")
                    next_gate = int(xx[0][1:]) - 1  
                    if dfs(next_gate):  
                        return True

        visited[gate_index] = 2  
        return False

    # Check each gate
    for i in range(len(output_pins)):
        if visited[i] == 0: 
            if dfs(i):  
                return True

    return False 

if detect_cycles(output_pins):
    output_file.write("Cycle detected in the circuit.")
    print("cycle detected int the circuit")
    output_file.close()
else:
    

    optimal_delay=sys.maxsize
    optimal_path=[]
    for f in range(1,len(gwh)):
        avght=max((totalh*f)//len(gwh),maxh)
        v=compute(avght,gwh_groups)
        allot_wire_delays(w_delay,v[0])
        x=critical_path(v[0],output_pins,g_delay)
    
        if(x[0]<optimal_delay):
            optimal_delay=x[0]
            bbwidth=v[1]
            bbheight=v[2]
            gates=v[3]
            optimal_path=x[1]
    if(len(gwh)==2 and len(wire_con)==1):
        if(optimal_delay!=0):
    
            optimal_delay=int(g_delay[0])+int(g_delay[1])
            
            out=wire_con[0][0]
            inp=wire_con[0][1]
        
            g_n,p_n=int(out.split(".")[0][1::])-1,int(out.split(".")[1][1::])-1
            g_n2,p_n2=int(inp.split(".")[0][1::])-1,int(inp.split(".")[1][1::])-1
            
            inp_c=pin_coord[g_n2][p_n2]
            out_c=pin_coord[g_n][p_n]
            if(inp_c[0]!=0):
                inp_c,out_c=out_c,inp_c
            if(inp_c[1]>out_c[1]):
            
                for i in gates:
                    if gates[i][0]==0:
                        
                        gates[i]=(gates[i][0],gates[i][1]+(inp_c[1]-out_c[1]))
            elif(inp_c[1]<out_c[1]):
            
                for i in gates:
                    if gates[i][0]!=0:
                        gates[i]=(gates[i][0],gates[i][1]+(-inp_c[1]+out_c[1]))
            for i in gates:
                for j in gwh:
                    if j[0]==i:
                        x=j[2]+gates[i][1]
            for k in gates:
                if k!=i:
                    for g in gwh:
                        if g[0]==k:
                            y=gates[k][1]+g[2]
            bbheight=max(x,y)
            
            
        
                    

    packing_percent=(totalarea*100/(bbwidth*bbheight))
    output_file.write("bounding_box"+" "+str(bbwidth)+" "+str(bbheight)+"\n")
    critical_path_str="critical_path "
    for i in optimal_path:
        critical_path_str=critical_path_str+i+" "
    output_file.write(critical_path_str+"\n")
        
    output_file.write("critical_path_delay"+" "+str(optimal_delay)+"\n")


        
    for i in gates:
        output_file.write(i+" "+str(gates[i][0])+" "+str(gates[i][1])+"\n")
        
    output_file.close()
    input_file.close()    

    print(packing_percent)
    endtime=time.time()
    print(endtime-startime,"seconds")

                   
               
               
               
        
    
                
                
        
    
                
                
    
    
    
    
            
            
                     
               
               
        
    
                
                
        
    
                
                
    
    
    
    
            
            
        
        
        
    
    

