print('\n\n\n')
print('********************************')
print('***Bem vindo ao jogo da forca***')
print('********************************')
print('\n\n\n')

palavra_secreta = 'banana'    

acertou = False
enforcou = False
while (not acertou and not enforcou):
    print('jogando...')
    chute = input('Qual letra?\n')
    posicao = 1
    for letra in palavra_secreta:
        if (chute.upper() == letra.upper()):
            print('Encontrei a letra {} na posição {}'.format(letra, posicao))
        posicao = posicao + 1

print('fim de jogo')

