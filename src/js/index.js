const images = [
    '../../images/a-cat-with-a-vampire-cape.svg',
    '../../images/black-white-illustration-bird-with-geometric-shapes-its-head-body.svg',
    '../../images/dog-that-has-sweater-it.svg',
    '../../images/floral-french-bulldog-portrait.svg',
    '../../images/portrait-animal-meditating-portrait.svg'
]

const img = document.querySelector('.image')
img.src = images[Math.floor(Math.random() * images.length)]

const indexButton = document.querySelector('.index-button')
indexButton.addEventListener('click', () => {
    window.open("upload.html", "_self");
})