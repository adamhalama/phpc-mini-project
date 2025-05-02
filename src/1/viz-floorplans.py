from pathlib import Path
from os.path import join
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
OUT_DIR  = Path("figures")
OUT_DIR.mkdir(exist_ok=True)

def load_domain_and_mask(bid):
    """Return (domain_grid, interior_mask) for one building ID."""
    dom = np.load(join(LOAD_DIR, f"{bid}_domain.npy"))       
    mask = np.load(join(LOAD_DIR, f"{bid}_interior.npy"))    
    return dom, mask

def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    # read ID list
    with open(join(LOAD_DIR, "building_ids.txt")) as f:
        ids = f.read().splitlines()[:N]

    for bid in ids:
        dom, mask = load_domain_and_mask(bid)

        fig, ax = plt.subplots(1, 2, figsize=(8, 3.5), constrained_layout=True)

        # --- left: domain grid (5 = blue, 25 = red, 0 = grey
        cmap_dom = matplotlib.colors.ListedColormap(["dimgray", "royalblue", "firebrick"])
        norm_dom = matplotlib.colors.BoundaryNorm([-1, 1, 10, 30], cmap_dom.N)
        ax[0].imshow(dom, cmap=cmap_dom, norm=norm_dom)
        ax[0].set_title(f"Domain grid (ID {bid})")
        ax[0].axis("off")

        # --- right: interior mask ---
        ax[1].imshow(mask, cmap="Greys_r", interpolation="nearest")
        ax[1].set_title("Interior mask")
        ax[1].axis("off")

        out_file = OUT_DIR / f"floorplan_{bid}.png"
        fig.savefig(out_file, dpi=150)
        plt.close(fig)
        print(f"Saved {out_file}")

if __name__ == "__main__":
    main()
