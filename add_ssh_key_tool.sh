#!/bin/bash

# Array to store IPs
declare -a IPS

# Create temp file for storing servers that don't have the key
> ./host/add_key

# Get user and keys
read -p "User [Ex. infra]: " user
read -p "Public key: " key

printf "\n\n"

# Validate if key already exists in authorized_keys
key_exist="cat /home/$user/.ssh/authorized_keys | grep -c \"$key\""

#Add key if it doesn't exists
space="\n"
key_treated="${space}${key}${space}"
add_key="printf \"$key_treated\" >> /home/$user/.ssh/authorized_keys"
counter=0

# Append a empty line in the end of the file
echo "" >> ./host/host.csv

# Iterate through rows in the first column
while IFS="," read -r server service hostname
do
    if [[ "$server" != "" ]]; then
        IPS+=("$server")
    fi
done < ./host/host.csv

# Cut all empty lines off file except one
cut_empty=$(sed -r '/^\s*$/d' ./host/host.csv); 
echo "$cut_empty"  > ./host/host.csv

# Connect via SSH and search for key in authorized_keys
for ip in "${IPS[@]}"; do
    has_public_key=$(sshpass -e ssh $user@$ip $key_exist)
    
    if [[ ${has_public_key} == "0" ]]; then
        echo "[$ip] - doesn't have key"
        echo "$ip" >> ./host/add_key
        counter=$((counter+1))

    elif [[ ${has_public_key} != "" ]]; then
        echo "[$ip] - has the key"
    else
        echo "Something went wrong"
        exit 1
    fi
done

# Confirm and Add key
if [[ $counter != 0 ]]; then
    printf "\nYou have $counter server(s) without your key!"

    read -p " Add?" choice
    if [[ "$choice" == "s" ]]; then
        printf "\nAdding key..\n"
        for ip in $(cat ./host/add_key); do
            sshpass -e ssh $user@$ip $add_key
            printf "\nYour key has been added to the server: $ip\n"
        done
    elif [[ "$choice" == "n" ]]; then
        printf "\nExiting..\n"
    else
        printf "\n\nPlease answer with [s] or [n], in lowercase.\n"
    fi
else
    printf "\n All the servers already have your key\n"
fi

rm -f ./host/add_key