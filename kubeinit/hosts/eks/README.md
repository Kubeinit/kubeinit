# Inventory files for EKS deployments

The inventory file(s) in this folder allow multiple cluster deployments in the same BM host.

As an example, the following steps are required to deploy a second (or as many are required) KubeInit clusters in the same host.

1. Duplicate the main inventory file.

```
echo "NEW_ID MUST BE AN INTEGER"
new_id=2
cp inventory inventory$new_id
```

2. Adjust network parameters.

The default internal network used is 10.0.0.0/24
so we need to change it to a new range.
In this case we will change from the range 10.0.0 to 10.0.<new_id>

```
sed -i "s/10\.0\.0/10\.0\.$new_id/g" inventory$new_id
```

3. Adjust the network and bridges names.

We will create new bridges and networks for the new
deployment.

```
sed -i "s/kimgtnet0/kimgtnet$new_id/g" inventory$new_id
sed -i "s/kimgtbr0/kimgtbr$new_id/g" inventory$new_id
sed -i "s/kiextbr0/kiextbr$new_id/g" inventory$new_id
```

4. Replace the hosts MAC addresses for new addresses.

We will randomly replace the MAC addresses for all
guest definitions. The following command will shuffle
the MAC addresses in the file each time is executed.
*Note:* awk does not suport hexa functions, and it  is
no possible to replace by colons.

```
awk -v seed="$RANDOM" '
  BEGIN { srand(seed) }
  { while(sub(/52:54:00:([[:xdigit:]]{1,2}:){2}[[:xdigit:]]{1,2}/,
              "52,,,54,,,00,,,"int(10+rand()*(99-10+1))",,,"int(10+rand()*(99-10+1))",,,"int(10+rand()*(99-10+1))));
    print > "tmp"
  }
  END { print "MAC shuffled" }
' "inventory$new_id"
mv tmp inventory$new_id
sed -i "s/,,,/:/g" inventory$new_id
```

5. Change the guest names.

VMs are cleaned everytime the host is provisioned, if their names are
not updated they will be removed every time.

```
sed -i "s/eks-/eks$new_id-/g" inventory$new_id
```

6. Run the deployment command using the new inventory file.

The deployment command should remain exactly as it was,
just update the reference to the new inventory file.

```
# Use the following inventory in your deployment command
-i ./hosts/eks/inventory$new_id
```

7. Cleaning up the host.

Just in case you need to clean things up.

```
for i in $(virsh -q list | awk '{ print $2 }'); do
  virsh destroy $i;
  virsh undefine $i --remove-all-storage;
done;
```
