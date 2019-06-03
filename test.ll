

define i32 @func.aa(i32 %b, i32 %n) {
    %b.ptr = alloca i32
    %n.ptr = alloca i32
    store i32 %b, i32* %b.ptr
    store i32 %n, i32* %n.ptr
    %n.1 = load i32, i32* %n.ptr
    ret i32 %n.1
}

define i32 @main() {
    %d.ptr = alloca [3 x i32]
    %n.ptr = alloca i32
    store i32 3, i32* %n.ptr
    %d.2.ptr = getelementptr inbounds [3 x i32], [3 x i32]* %d.ptr, i32 0, i32 0
    store i32 1, i32* %d.2.ptr
    %d.3.ptr = getelementptr inbounds [3 x i32], [3 x i32]* %d.ptr, i32 0, i32 1
    %d.4.ptr = getelementptr inbounds [3 x i32], [3 x i32]* %d.ptr, i32 0, i32 0
    %d.4.5 = load i32, i32* %d.4.ptr
    %buffer6 = add i32 %d.4.5, 1
    store i32 %buffer6, i32* %d.3.ptr
    %d.7.ptr = getelementptr inbounds [3 x i32], [3 x i32]* %d.ptr, i32 0, i32 2
    store i32 3, i32* %d.7.ptr
    %res.ptr = alloca i32
    %d.8 = load i32, i32* %d.ptr
    %n.9 = load i32, i32* %n.ptr
    %aa.10 = call i32 @func.aa(i32 %d.8, i32 %n.9)
    store i32 %aa.10, i32* %res.ptr
    %res.11 = load i32, i32* %res.ptr
    %buffer13 = getelementptr inbounds [4 x i8], [4 x i8]* @.str.1, i32 0, i32 0 
    call i32 (i8*, ...) @printf(i8* %buffer13, i32 %res.11)
    ret i32 0
}

declare i32 @printf(i8*, ...)
@.str.1 = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
