const makeSpinner = () => {
    const spinner = document.createElement('div');
    const spinnerImage = document.createElement('img');
    spinner.classList.add('load');
    spinnerImage.setAttribute('src', '/static/image/loading.gif');
    spinner.appendChild(spinnerImage);
    return spinner;
};

const makeSkeleton = () => {
    const skeleton = document.createElement('li');
    const skeletonImage = document.createElement('div');
    const skeletonText = document.createElement('p');
    skeleton.classList.add('skeleton');
    skeletonImage.classList.add('skeleton__image');
    skeletonText.classList.add('skeleton__text');
    skeletonText.textContent = ' ';
    skeleton.appendChild(skeletonImage);
    skeleton.appendChild(skeletonText);
    return skeleton;
};