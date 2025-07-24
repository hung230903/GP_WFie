import pandas as pd

df = pd.read_csv('wifi_data.csv')
df['SSID'] = df['SSID'].fillna('')

filtered_df = df[df['SSID'].str.startswith(('USTH', 'ICT'))]

ssids_to_number = ['USTH_Student', 'USTH_Guest', 'USTH_Office', 'USTH_MGMT']

filtered_df['SSID'] = filtered_df.groupby(['X Position', 'Y Position', 'SSID']).apply(
    lambda x: x.assign(
        SSID=lambda df: [
            f"{ssid}{i+1}" if ssid in ssids_to_number else ssid
            for i, ssid in enumerate(df['SSID'])
        ]
    )
).reset_index(drop=True)['SSID']

filtered_df.to_csv('new_data.csv', index=False)

