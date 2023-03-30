import discord, asyncio, time, requests
from datetime import datetime
from bs4 import BeautifulSoup
from discord.ext import commands
from discord.utils import get

client = discord.Client()
client = commands.Bot(command_prefix="!")

Zoznam = []
Zoznam1 = []
Zoznam2 = []
sprava = None
url = None
zoznamproduktov = None
guild = None
channel = None
vyberproduktu = False
ukoncit_cyklus = False
#________________________________________________________________________________________________________________________________________________________________
@client.event
async def on_ready():
	print('FUNGUJEM!')
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Heureka.sk"))

#________________________________________________________________________________________________________________________________________________________________
@client.command()
async def find(ctx,*,message):
	get_server(ctx)
	global url, vyberproduktu, zoznamproduktov
	if('https://' in message):
		url = message
		await ctx.message.delete()
		#----------------------------
		if "heureka.sk" in url:
			await main()
		else:
			zlylink = await ctx.channel.send("URL musí byť z eshopu Heureka.sk")
			await asyncio.sleep(5)
			await zlylink.delete()
		#----------------------------
	else:
		if vyberproduktu == True:
			await ctx.message.delete()

			if (message.isnumeric()) and (int(message)>=1) and (int(message)<=3):
				await zoznamproduktov.delete()
				url = Zoznam2[int(message)-1]
				await main()
				vyberproduktu = False

		else:
			url = 'https://www.heureka.sk/?h%5Bfraze%5D='+message

			await ctx.message.delete()
			hladanie(url)
			#----------------------------
			if len(Zoznam1) <= 0 :
				neexistuje = await ctx.channel.send("Produkt s takýmto názvom neexistuje.")
				await asyncio.sleep(5)
				await neexistuje.delete()
			else:
				produkty = ''
				cislopolozky=0
				for i in Zoznam1:
					cislopolozky+=1
					produkty = produkty+'**'+str(cislopolozky)+'.  '+'**'+i[0]+'\n'
				zoznamproduktov = await ctx.channel.send('>>> ' +'**Vyberte jednu z možností príkazom**'+'``!find 1-3``'+'\n'+produkty)
				vyberproduktu = True
			#----------------------------

#________________________________________________________________________________________________________________________________________________________________
@client.command()
async def reset(ctx):
	global ukoncit_cyklus
	await ctx.message.delete()
	wait = await ctx.channel.send("Je potrebné počkať kým sa dokončí cyklus")
	await asyncio.sleep(8)
	await wait.delete()
	ukoncit_cyklus = True

#________________________________________________________________________________________________________________________________________________________________
@client.command()
@commands.is_owner()
async def clear(ctx):
	if ctx.channel.id is not channel.id:
		return
	await clear(10)

#________________________________________________________________________________________________________________________________________________________________
@client.command()
@commands.is_owner()
async def quit(ctx):
	if ctx.channel.id is not channel.id:
		return
	await clear(2)
	await ctx.bot.logout()

#________________________________________________________________________________________________________________________________________________________________
@client.event
async def main():
	hodnoty = nacitaniehodnot()
	y = hodnoty[2]
	rola = get(guild.roles, name='HeurekaCheck')
	global sprava, ukoncit_cyklus

	while True:

		datum = datetime.now().strftime("%d/%m/%Y \n%H:%M")
		hodnoty = nacitaniehodnot()
		produkt = hodnoty[0]
		obrazok = hodnoty[1]
		pocetpoloziek = hodnoty[2]

		if (pocetpoloziek > 1) or (pocetpoloziek == 0):
			obchod_gramatika="obchodoch."
		else:
			obchod_gramatika="obchode."
			
		shopy = ''
		cennik = ''
		for i in Zoznam:
			shopy = shopy+i[0]+'\n'
			cennik = cennik+i[1]+'\n'

		embed = discord.Embed(title=produkt, description = "Tento produkt je dostupný v "+str(pocetpoloziek)+" "+obchod_gramatika ,color= 0x008FFF)
		embed.set_thumbnail(url=obrazok)
		embed.set_author(name='Heureka', url=url,icon_url="https://i1.wp.com/blog.heureka.sk/wp-content/uploads/2019/12/cropped-lupa_heureka_rgb-01.png?fit=512%2C512&ssl=1&w=640")
		embed.add_field(name="Obchod", value=shopy, inline=True)
		embed.add_field(name="Cena", value=cennik, inline=True)
		embed.set_footer(text=datum)

		if pocetpoloziek != y and sprava is not None:
			await sprava.delete()
			sprava = await channel.send(embed=embed) 
			mention = await channel.send(f"{rola.mention}")
			await mention.delete()
			y=pocetpoloziek
		elif not sprava:
			sprava = await channel.send(embed=embed)
		await asyncio.sleep(120)

		if ukoncit_cyklus == True:
			koniec = await channel.send("Cyklus sa úspešne ukončil")
			ukoncit_cyklus = False
			await sprava.delete()
			sprava = None
			await asyncio.sleep(5)
			await koniec.delete()
			break	

#________________________________________________________________________________________________________________________________________________________________
def nacitaniehodnot():
	print('xyx')
	pocet=0
	Zoznam.clear()
	soup = BeautifulSoup(requests.get(url).content, features="html.parser")

	for x in soup.find_all(attrs={"c-offer-v3 js-offer"}):
		if pocet >= 10:
			break
		pocet+=1
		cena = x.find(attrs={"class": "c-offer-v3__price u-bold u-delta"})
		shopy = x.find(attrs={"class": "c-offer-v3__shop-name js-exit-link u-color-text-light u-milli u-align-center"})
		shopurl = shopy['href']
		
		shop = "["+shopy.text.strip()+"]"+"("+shopurl+")" 
		Zoznam.append([shop,cena.text.strip()])

	for i in soup.find_all(attrs={"class": "u-bold u-gamma c-product-info__name"}):
		produkt = (i.text.strip())
	for i in soup.find_all("img", attrs={"class": "c-gallery-open__thumbnail"}):
		obrazok = (i['src'])

	pocetpoloziek = 0
	soup1 = BeautifulSoup(requests.get('https://www.heureka.sk/?h%5Bfraze%5D='+produkt).content, features="html.parser")
	for x in soup1.find(attrs={"class": "c-product__shops c-product__link"}):
		y = x.text
		if "obchodoch" in y:
			pocetpoloziek = y.strip("vobchodoch").replace(" ","")
		else:
			pocetpoloziek = 1

	#	return[list]  0,1,2,3,4
	return[produkt,obrazok,int(pocetpoloziek),Zoznam]

#________________________________________________________________________________________________________________________________________________________________
def hladanie(url):
	Zoznam1.clear()
	Zoznam2.clear()
	i=3
	soup = BeautifulSoup(requests.get(url).content, features="html.parser")
	for x in soup.find_all(attrs={"class": "c-product-list__item"}):
		if i == 0:
			break
		i-=1
		produkty = x.find(attrs={"class": "c-product__link"})
		produkturl = produkty['href']
		Zoznam1.append([produkty.text.strip()])
		Zoznam2.append(produkturl)
	return[Zoznam1,Zoznam2]

#________________________________________________________________________________________________________________________________________________________________
async def clear(l):
	await channel.purge(limit=l, check=lambda msg: not msg.pinned)

#________________________________________________________________________________________________________________________________________________________________
def get_server(ctx):
	global channel, guild
	guild = client.get_guild(ctx.guild.id)
	c = discord.utils.get(ctx.guild.channels, name="heureka")
	channel = client.get_channel(c.id)



client.run('ODM1NjE3OTM3Nzc5NTg5MTgw.YISD2Q.yIDl5jndZ3FiO33gddtwPl4k6aA')